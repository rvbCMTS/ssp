from datetime import datetime as dt
from django.contrib import messages
from django.forms import ValidationError
from django.db.models import Count, Avg, Sum, F
from django.db.models.functions import TruncYear
from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import render, redirect, HttpResponse, Http404
from django.utils.translation import gettext as _
from datetime import date, time, datetime as dt, timedelta
import json
from math import floor, isnan
import numpy as np
import pandas as pd
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from statistics import median
from typing import Optional

from .forms import FluoroTimeForm
from .helpers import fluoro_dose_convert
from .models import Exam, Operator, Clinic, Hospital, AnatomyRegion, Modality, ModalityClinicMap, OperatorClinicMap, DirtyClinic, DirtyModality, DirtyOperator, ExamDescription
from .tools.update_fluoro_times import OrbitGML


def index(request):

    return render(request=request, template_name='fluoro_times/index.html')


def yearly_reports(request):
    years = Exam.objects.annotate(year=TruncYear('exam_date')).order_by('-year').values('year')

    clinics = Exam.objects.annotate(
        year=TruncYear('exam_date'),
        clinic=F('dirty_clinic__clinic__name'),
        hospital=F('dirty_clinic__clinic__hospital__name'),
        clinic_id=F('dirty_clinic__clinic_id')).filter(
        dirty_clinic__clinic__isnull=False).order_by('clinic', '-year').values(
        'clinic_id', 'clinic', 'hospital', 'year').distinct()

    output = {str(obj['year'].year): {} for obj in years}
    for obj in clinics:
        output[str(obj['year'].year)][str(obj['clinic_id'])] = f"{obj['clinic']} - {obj['hospital']}"

    context = {
        'filter': json.dumps(output)
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


def register_exam_form(request, clinic: Optional[int] = None):
    if request.method == 'POST':
        form = FluoroTimeForm(request.POST)
        if form.is_valid():
            if Exam.objects.filter(exam_no=form.cleaned_data.get('exam_id')).all() is not None:
                raise ValidationError(_('Undersökningmed id %(value)'), code='invalid',
                                      params={'value': form.cleaned_data.get('exam_id')})

            dirty_clinic = DirtyClinic.objects.filter(clinic=form.cleaned_data.get('clinic')).first()
            if dirty_clinic is None:
                dirty_clinic = DirtyClinic(
                    dirty_name=f"{form.cleaned_data.get('clinic').name} - {form.cleaned_data.get('clinic').hospital}",
                    clinic=form.cleaned_data.get('clinic'))
                dirty_clinic.save()

            dirty_operator = DirtyOperator.objects.filter(operator=form.cleaned_data.get('operator')).first()
            if dirty_operator is None:
                dirty_operator = DirtyOperator(
                    dirty_name=f"{form.cleaned_data.get('operator').last_name}, {form.cleaned_data.get('operator').first_name}",
                    operator=form.cleaned_data.get('operator')
                )
                dirty_operator.save()

            dirty_modality = DirtyModality.objects.filter(modality=form.cleaned_data.get('modality')).first()
            if dirty_modality is None:
                dirty_modality = DirtyModality(
                    dirty_name=form.cleaned_data.get('modality').name,
                    operator=form.cleaned_data.get('modality')
                )
                dirty_modality.save()

            exam_description = ExamDescription.objects.filter(
                description=form.cleaned_data.get('anatomical_region').region,
                pediatric=int(form.cleaned_data.get('pediatric')) == 2).first()
            if exam_description is None:
                exam_description = ExamDescription(
                    description=form.cleaned_data.get('anatomical_region').region,
                    anatomy_region=form.cleaned_data.get('anatomical_region'),
                    pediatric=int(form.cleaned_data.get('pediatric')) == 2
                )
                exam_description.save()

            fluoro_time = 0
            if form.cleaned_data.get('fluoro_time_minutes') is not None:
                fluoro_time += form.cleaned_data.get('fluoro_time_minutes') * 60
            if form.cleaned_data.get('fluoro_time_seconds') is not None:
                fluoro_time += form.cleaned_data.get('fluoro_time_seconds')

            fluoro_dose = 0
            if form.cleaned_data.get('fluoro_dose') is not None:
                fluoro_dose = fluoro_dose_convert(
                    form.cleaned_data.get('fluoro_dose'),
                    form.cleaned_data.get('fluoro_dose_unit')
                )

            fluoro_exam = Exam(
                exam_no=form.cleaned_data.get('exam_id'),
                exam_description=exam_description,
                exam_date=form.cleaned_data.get('exam_date'),
                dirty_clinic=dirty_clinic,
                dirty_operator=dirty_operator,
                dirty_modality=dirty_modality,
                fluoro_time=fluoro_time,
                dose=fluoro_dose
            )

            fluoro_exam.save()
            messages.success(request=request,
                             message=f'Genomlysningsundersökningen {form.cleaned_data.get("exam_id")} har sparats')

    cmm = ModalityClinicMap.objects.all().prefetch_related()
    modality_map = {}
    if len(cmm) > 0:
        for obj in cmm:
            if str(obj.clinic.id) not in modality_map.keys():
                modality_map[str(obj.clinic.id)] = []
            modality_map[str(obj.clinic.id)].append(obj.modality.id)

    com = OperatorClinicMap.objects.all().prefetch_related()
    operator_map = {}
    if len(com) > 0:
        for obj in com:
            if str(obj.clinic.id) not in operator_map.keys():
                operator_map[str(obj.clinic.id)] = []
            operator_map[str(obj.clinic.id)].append(obj.operator.id)

    mdu = Modality.objects.all()
    modality_dose_unit = {}
    if len(mdu) > 0:
        modality_dose_unit = {obj.id: obj.dose_unit for obj in mdu}

    form = FluoroTimeForm(initial={'clinic': clinic})

    context = {
        'preset_clinic': clinic,
        'clinic_operator_map': json.dumps(operator_map),
        'clinic_modality_map': json.dumps(modality_map),
        'modality_dose_unit': json.dumps(modality_dose_unit),
        'form': form
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
        # anatomy_regions = list(reversed(sorted(anatomy_regions)))
        anatomy_regions = list(sorted(anatomy_regions))

        # Get pie chart data
        pie_chart_query = Exam.objects.select_related(
            'exam_description__anatomy_region'
        ).filter(
            exam_date__gte=dt(year=dt.now().year - 1, month=1, day=1)
        ).annotate(
            year=TruncYear('exam_date')
        ).values('year', 'exam_description__anatomy_region__region').annotate(exams=Count('exam_no')).order_by(
            'year', 'exam_description__anatomy_region__region',
        ).all()

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
        query = Exam.objects.select_related('exam_description__anatomy_region').filter(
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

        median_plot_current = [None] * len(anatomy_regions)
        median_plot_previous = [None] * len(anatomy_regions)
        for _, row in median_data.iterrows():
            if row.exam_description__anatomy_region__region is None:
                ar = 'Okänd'
            else:
                ar = row.exam_description__anatomy_region__region
            if row.year == current_year:
                median_plot_current[anatomy_regions.index(ar)] = dt.combine(dt.date(dt.now()), time(
                    minute=int(floor(row.total_fluoro_time)),
                    second=int((row.total_fluoro_time - floor(row.total_fluoro_time)) * 60))
                )
            else:
                median_plot_previous[anatomy_regions.index(ar)] = dt.combine(dt.date(dt.now()), time(
                    minute=int(floor(row.total_fluoro_time)),
                    second=int((row.total_fluoro_time - floor(row.total_fluoro_time))*60))
                )

        # Format response data
        context = {
            'pieChart': {
                'previousYear': {'labels': anatomy_regions, 'values': pie_previous_year, 'type': 'pie', 'hole': 0.4,
                                 'hoverinfo': 'label+percent+name', 'textinfo': 'none', 'name': str(current_year - 1),
                                 'sort': False},
                'currentYear': {'labels': anatomy_regions, 'values': pie_current_year, 'type': 'pie', 'hole': 0.4,
                                 'hoverinfo': 'label+percent+name', 'textinfo': 'none', 'name': str(current_year),
                                 'sort': False}
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
            if row['count'] < 1:
                context['tableData'][row.exam_description__anatomy_region__region][
                    row.dirty_clinic__clinic__hospital__name]['count'] = None
                context['tableData'][row.exam_description__anatomy_region__region][
                    row.dirty_clinic__clinic__hospital__name][
                    'median_time'] = None
            else:
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
                    title='Mediantid (hh:mm:ss)',
                    type='time',
                    tickformat='%H:%M:%S'
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


class YearlyReportData(APIView):
    """
    Handle AJAX requests for data for yearly reports
    """
    permission_classes = (permissions.AllowAny, )

    def get(self, request, format=None):
        year = self.request.query_params.get('year', None)
        clinic = self.request.query_params.get('clinic', None)
        if year is None or clinic is None:
            return Response()
        clinic_name = Clinic.objects.get(pk=clinic)

        query = Exam.objects.all().filter(
            exam_date__gte=dt(year=int(year) - 4, month=1, day=1),
            exam_date__lte=dt(year=int(year), month=12, day=31),
            dirty_clinic__clinic_id=int(clinic)
        ).values('exam_no', 'exam_date', 'dirty_operator__operator__first_name', 'dirty_operator__operator__last_name',
                 'exam_description__anatomy_region__region', 'fluoro_time')

        # Create a pandas data frame from the query response
        df = pd.DataFrame(list(query))
        df.rename(index=str,
                  columns={'exam_no': 'ExamNo', 'exam_date': 'ExamDate',
                           'dirty_operator__operator__first_name': 'FirstName',
                           'dirty_operator__operator__last_name': 'LastName',
                           'exam_description__anatomy_region__region': 'AnatomyRegion',
                           'fluoro_time': 'FluoroTime'},
                  inplace=True)

        df.AnatomyRegion[df.AnatomyRegion.isnull()] = 'Ej Klacificerat'
        df.FirstName[df.FirstName.isnull()] = '<Förnamn>'
        df.LastName[df.LastName.isnull()] = '<Efternamn>'

        # Anatomy region statistics

        anatomy_region_data = operator_statistic_data = df[df.ExamDate.dt.year == int(year)]

        anatomy_region_data = anatomy_region_data.groupby(['ExamNo', 'AnatomyRegion'], as_index=False).agg(
            {'FluoroTime': sum})

        anatomy_region_data = anatomy_region_data.groupby('AnatomyRegion').agg(
            {'FluoroTime': ['count', 'median', lambda x: np.percentile(x, q=95)]})
        anatomy_region_table = [[
            ar, row['FluoroTime']['count'],
            time(hour=int(floor(row['FluoroTime']['median'] / 60)),
                 minute=int(floor(row['FluoroTime']['median'] - floor(row['FluoroTime']['median'] / 60))),
                 second=int((row['FluoroTime']['median'] - floor(row['FluoroTime']['median'])) * 60)),
            time(hour=int(floor(row['FluoroTime']['<lambda>'] / 60)),
                 minute=int(floor(row['FluoroTime']['<lambda>'] - floor(row['FluoroTime']['<lambda>'] / 60))),
                 second=int((row['FluoroTime']['<lambda>'] - floor(row['FluoroTime']['<lambda>'])) * 60))
        ] for ar, row in anatomy_region_data.iterrows()]

        # Operator statistics

        operator_statistic_data.loc[:, 'Operator'] = list(operator_statistic_data[['LastName', 'FirstName']].apply(lambda x: ', '.join(x), axis=1))
        operator_statistic_data = operator_statistic_data.groupby(['ExamNo', 'Operator'], as_index=False).agg(
            {'FluoroTime': sum})
        operator_statistic_data = operator_statistic_data.groupby('Operator').agg(
            {'FluoroTime': ['count', 'sum', 'median', lambda x: np.percentile(x, q=95)]})
        operator_table = [[
            op, row['FluoroTime']['count'],
            time(hour=int(floor(row['FluoroTime']['sum'] / 60)),
                 minute=int(floor(row['FluoroTime']['sum'] - floor(row['FluoroTime']['sum'] / 60))),
                 second=int((row['FluoroTime']['sum'] - floor(row['FluoroTime']['sum'])) * 60)),
            time(hour=int(floor(row['FluoroTime']['median'] / 60)),
                 minute=int(floor(row['FluoroTime']['median'] - floor(row['FluoroTime']['median'] / 60))),
                 second=int((row['FluoroTime']['median'] - floor(row['FluoroTime']['median'])) * 60)),
            time(hour=int(floor(row['FluoroTime']['<lambda>'] / 60)),
                 minute=int(floor(row['FluoroTime']['<lambda>'] - floor(row['FluoroTime']['<lambda>'] / 60))),
                 second=int((row['FluoroTime']['<lambda>'] - floor(row['FluoroTime']['<lambda>'])) * 60))
        ] for op, row in operator_statistic_data.iterrows()]

        # Bubble plot

        df = df.groupby(['ExamNo', 'ExamDate', 'AnatomyRegion'], as_index=False).agg({'FluoroTime': sum})

        df.ExamDate = df.ExamDate.dt.year

        df_count = df.groupby(['ExamDate', 'AnatomyRegion'], as_index=False).agg({'FluoroTime': 'count'})
        df = df.groupby(['ExamDate', 'AnatomyRegion'], as_index=False).agg({'FluoroTime': median})

        plot = dict()
        x = list(set(df.ExamDate))
        for _, row in df.iterrows():
            plot.setdefault(row.AnatomyRegion,
                            {
                                'x': x.copy(),
                                'y': [None] * len(x),
                                'name': row.AnatomyRegion,
                                'mode': 'markers',
                                'marker': {
                                    'size': [None] * len(x),
                                    'sizemode': 'area',
                                    'opacity': 0.6
                                }})
            plot[row.AnatomyRegion]['y'][x.index(row.ExamDate)] = dt.combine(dt.date(dt.now()), time(
                hour=int(floor(row['FluoroTime'] / 60)),
                minute=int(floor(row['FluoroTime'] - floor(row['FluoroTime'] / 60))),
                second=int((row['FluoroTime'] - floor(row['FluoroTime'])) * 60)))

        # Set the marker size
        for _, row in df_count.iterrows():
            plot[row.AnatomyRegion]['marker']['size'][x.index(row.ExamDate)] = row.FluoroTime

        for _, row in plot.items():
            row['text'] = [f"Antal:{row['marker']['size'][ind]}" for ind in range(len(row['y']))]

        layout = {
            'title': 'Mediangenomlysningstid per år och område',
            'showlegend': True,
            'legend': {
                'orientation': 'h'
            },
            'xaxis': {
                'tickmode': 'linear',
                'tick0': min(df.ExamDate),
                'dtick': 1,
                'title': 'År'
            },
            'yaxis': {
                'title': 'Mediantid (h:min:s)',
                'rangemode': 'tozero',
                'type': 'time',
                'tickformat': '%H:%M:%S'
            }
        }
        layout2 = {}

        return Response({
            'reportHeader': f'Årsrapport {year} för {clinic_name.name}',
            'operatorTable': {'tableId': 'idOperatorStat', 'data': operator_table},
            'anatomyRegionTable': {'tableId': 'idAreaStat', 'data': anatomy_region_table},
            'bubblePlot': {'id': 'idBubblePlot', 'data': [obj for _, obj in plot.items()],
                           'layout': layout, 'layout2': layout2, 'cols': len(x), 'maxCount': max(df_count.FluoroTime)}
        })


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
