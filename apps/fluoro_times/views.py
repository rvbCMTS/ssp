from datetime import datetime as dt
from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncYear
from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from datetime import date, time, datetime as dt, timedelta
from math import floor, isnan
import numpy as np
import pandas as pd
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from statistics import median

from .models import Exam, Operator, Clinic, Hospital, AnatomyRegion
from .tools.update_fluoro_times import OrbitGML
from .serializers import ExamSummarySerializer


def index(request):

    return render(request=request, template_name='fluoro_times/index.html')


def yearly_reports(request):
    years = Exam.objects.annotate(year=TruncYear('exam_date')).order_by('-year').values('year')

    clinics = Clinic.objects.order_by('name').all()
    clinics = [{'id': obj.pk, 'name': f'{obj.name} - {obj.hospital.name}'} for obj in clinics]

    context = {
        'years': years,
        'clinics': clinics,
    }

    return render(request=request, template_name='fluoro_times/yearly_report.html', context=context)


def ssm_plots(request):
    """
    View that plots the number of exams and mean exam time per year for the last 5 years
    """
    # Get data from db
    q1 = Exam.objects.filter(
        exam_date__gte=date(int(dt.strftime(dt.now(), '%Y'))-6, 1, 1),
        exam_date__lt=date(int(dt.strftime(dt.now(), '%Y'))-1, 1, 1)
    ).annotate(year=TruncYear('exam_date'), anatomy_region='exam_description__anatomy_region__region').values(
        'year', 'anatomy_region').order_by('year', 'anatomy_region').values('year', 'anatomy_region', 'fluoro_time')

    db_data = pd.DataFrame.from_records(q1)

    # Get the number of exams per year grouped by anatomy region for the last 5 whole years
    exam_counts = Exam.objects.filter(
        exam_date__gte=date(int(dt.strftime(dt.now(), '%Y'))-6, 1, 1),
        exam_date__lt=date(int(dt.strftime(dt.now(), '%Y'))-1, 1, 1)
    ).annotate(
        year=TruncYear('exam_date'),
        anatomy_region='exam_description__anatomy_region__region').values(
        'year', 'anatomy_region').aggregate(num_exams=Count('anatomy_region')).order_by(
        'year', 'anatomy_region').values('year', 'anatomy_region', 'fluoro_time')

    anatomy_regions = list(set([obj.anatomy_region for obj in exam_counts]))
    years = list(set([obj.year.year for obj in exam_counts]))

    plot_data = {}
    for year in years:
        plot_data[str(year)] = {
            'x': anatomy_regions,
            'y': [None]*len(anatomy_regions),
            'name': str(year),
            'type': 'bar',
            'orientation': 'h'
        }

    for obj in exam_counts:
        plot_data[str(obj.year.year)]['y'][anatomy_regions.index(obj.anatomy_region)] = obj.num_exams

    context = {'examsPerYear': {
        'data': [obj for obj in plot_data],
        'layout': {'barmode': 'group'}
    }}

    # Get the median fluoroscopy time per year grouped by anatomy region for the last 5 whole years
    exam_counts = Exam.objects.filter(
        exam_date__gte=date(int(dt.strftime(dt.now(), '%Y')) - 6, 1, 1),
        exam_date__lt=date(int(dt.strftime(dt.now(), '%Y')) - 1, 1, 1)
    ).annotate(
        year=TruncYear('exam_date'),
        anatomy_region='exam_description__anatomy_region__region').values(
        'year', 'anatomy_region').aggregate(num_exams=Count('anatomy_region')).order_by(
        'year', 'anatomy_region').values('year', )

    anatomy_regions = list(set([obj.anatomy_region for obj in exam_counts]))
    years = list(set([obj.year for obj in exam_counts]))

    plot_data = {}
    for year in years:
        plot_data[str(year)] = {
            'x': anatomy_regions,
            'y': [None] * len(anatomy_regions),
            'name': str(year),
            'type': 'bar',
            'orientation': 'h'
        }

    for obj in exam_counts:
        plot_data[str(obj.year)]['y'][anatomy_regions.index(obj.anatomy_region)] = obj.num_exams

    context['medianTimePerYear'] = {
        'data': [obj for obj in plot_data],
        'layout': {'barmode': 'group'}
    }

    return render(request=request, template_name='fluoro_times/ssm_report.html', context=context)


def data_cleaning(request):

    return render(request=request, template_name='fluoro_times/clean_data.html')


def register_exam_form(request):

    context = {
        'clinics': [{'id': 1, 'name': 'Test Klinik'}, ],
        'modalities': [{'id': 1, 'name': 'Testmodalitet'}, ],
        'operators': [{'id': 1, 'name': 'Efternamn, Förnamn'}, ],

        'preset_clinic': None,
        'clinic_operator_map': [{"1": [1, 2, 3, 4]}],
        'clinic_modality_map': [{"1": [1]}]
    }
    return render(request=request, template_name='fluoro_times/manual_report_form.html', context=context)


def api_save_new_exam(request):
    result = {}
    return JsonResponse(result)


def api_save_clean_data(request):
    result = {}
    return JsonResponse(result)


class IndexSummaryData(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, format=None):
        current_year = dt.now().year

        query = Hospital.objects.all().filter(active=True)

        if not query:
            return Response()
        #hospitals = {obj.name: {} for obj in query}
        hospitals = list(set([obj.name for obj in query]))

        # Get a list of distinct anatomy regions
        anatomy_regions = AnatomyRegion.objects.all()
        anatomy_regions = list(set([obj.region for obj in anatomy_regions]))
        anatomy_regions.append('Okänd')
        anatomy_regions = list(reversed(sorted(anatomy_regions)))

        # Get pie chart data
        pie_chart_query = Exam.objects.all().filter(
            exam_date__gte=dt(year=dt.now().year - 1, month=1, day=1)
        ).annotate(
            year=TruncYear('exam_date')
        ).values('year', 'exam_description__anatomy_region__region').annotate(exams=Count('exam_no')).order_by(
            'year', 'exam_description__anatomy_region__region',
        )

        if not pie_chart_query:
            return Response()
        pie_current_year = [0] * len(anatomy_regions)
        pie_previous_year = [0] * len(anatomy_regions)
        for obj in pie_chart_query:
            if obj['exam_description__anatomy_region__region'] is None:
                ar = 'Okänd'
            else:
                ar = obj['exam_description__anatomy_region__region']
            if current_year == obj['year'].year:
                pie_current_year[anatomy_regions.index(ar)] = obj['exams']
            else:
                pie_previous_year[anatomy_regions.index(ar)] = obj['exams']

        # Get median fluoro time data per anatomy region and year
        query = Exam.objects.all().filter(
            exam_date__gte=dt(year=dt.now().year - 1, month=1, day=1)
        ).annotate(
            year=TruncYear('exam_date')
        ).values(
            'year', 'exam_description__anatomy_region__region', 'exam_no'
        ).annotate(
            total_fluoro_time=Sum('fluoro_time')
        ).values('year', 'exam_description__anatomy_region__region', 'total_fluoro_time')

        if not query:
            return Response()

        median_data = pd.DataFrame(list(query))
        median_data.year = median_data.year.dt.year
        median_data = median_data.groupby(
            ['year', 'exam_description__anatomy_region__region']
        ).agg({'total_fluoro_time': median}).reset_index()

        median_plot_current = median_plot_previous = [None] * len(anatomy_regions)
        for _, row in median_data.iterrows():
            if row.exam_description__anatomy_region__region is None:
                ar = 'Okänd'
            else:
                ar = row.exam_description__anatomy_region__region
            if row.year == current_year:
                median_plot_current[anatomy_regions.index(ar)] = time(
                    minute=int(floor(row.total_fluoro_time)),
                    second=int((row.total_fluoro_time - floor(row.total_fluoro_time)) * 60)
                )
            else:
                median_plot_previous[anatomy_regions.index(ar)] = time(
                    minute=int(floor(row.total_fluoro_time)),
                    second=int((row.total_fluoro_time - floor(row.total_fluoro_time))*60)
                )

        # Format response data
        context = {
            'pieChart': {
                'previousYear': {'labels': anatomy_regions, 'values': pie_previous_year, 'type': 'pie', 'hole': 0.4,
                                 'hoverinfo': 'label+percent+name', 'textinfo': 'none', 'name': str(current_year - 1)},
                'currentYear': {'labels': anatomy_regions, 'values': pie_current_year, 'type': 'pie', 'hole': 0.4,
                                 'hoverinfo': 'label+percent+name', 'textinfo': 'none', 'name': str(current_year)}
            },
            'medianPlot': [
                {'y': anatomy_regions, 'x': median_plot_previous, 'name': f'{current_year - 1}', 'type': 'bar',
                 'orientation': 'h'},
                {'y': anatomy_regions, 'x': median_plot_current, 'name': f'{current_year}', 'type': 'bar',
                 'orientation': 'h'}
            ]
        }

        # Get median fluoro time data per anatomyregion and hospital for current year
        query = Exam.objects.all().filter(
            exam_date__gte=dt(year=dt.now().year, month=1, day=1)
        ).values(
            'exam_description__anatomy_region__region', 'dirty_clinic__clinic__hospital__name', 'exam_no'
        ).annotate(
            total_fluoro_time=Sum('fluoro_time')
        ).values('exam_description__anatomy_region__region', 'dirty_clinic__clinic__hospital__name', 'total_fluoro_time')

        if not query:
            return Response()

        median_clinic_data = pd.DataFrame(list(query))
        median_clinic_data.replace(np.nan, 'Okänd', regex=True, inplace=True)
        median_clinic_data = median_clinic_data.groupby(
            ['exam_description__anatomy_region__region', 'dirty_clinic__clinic__hospital__name']
        ).total_fluoro_time.agg(['median', 'count']).reset_index()

        hospitals = list(set(hospitals + list(median_clinic_data.dirty_clinic__clinic__hospital__name.unique())))
        context['tableData'] = {ar: {hospital: {'count': int(), 'median_time': float()} for hospital in hospitals} for
                                ar in anatomy_regions}
        for _, row in median_clinic_data.iterrows():
            context['tableData'][row.exam_description__anatomy_region__region][
                row.dirty_clinic__clinic__hospital__name]['count'] = row['count']
            context['tableData'][row.exam_description__anatomy_region__region][
                row.dirty_clinic__clinic__hospital__name][
                'median_time'] = f"{floor(row['median']):02}:{round((row['median'] - floor(row['median'])) * 60):02}"

        # Create layouts for the plots
        context['layouts'] = {
            'medianPlot': {
                'title': 'Median-genomlysningstid per område',
                'barmode': 'group',
                'margin': {
                    'l': 100,
                    'r': 50,
                    'b': 80,
                    't': 80,
                    'pad': 4
                },
                'xaxis': dict(
                    title='Mediantid (hh:mm:ss)'
                )
            },
            'pieCharts': {
                'currentYear': {
                    'title': f"Innevarande år ({sum(context['pieChart']['currentYear']['values'])} undersökningar)",
                },
                'previousYear': {
                    'title': f"Föregående år ({sum(context['pieChart']['previousYear']['values'])} undersökningar)"
                }
            },
            'medianHeight': len(anatomy_regions)
        }

        return Response(context)


def api_update_orbit_data(request):
    gml = OrbitGML()
    try:
        gml.fetch_orbit_data()
        gml.format_data()
        gml.assert_new_in_db()
        gml.insert_into_sspdb()
        return redirect('gml:index')
    except:
        return HttpResponseServerError('Kunde inte slutföra uppdateringen av genomlysningsdata')
