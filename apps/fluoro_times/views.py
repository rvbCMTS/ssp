from django.db.models import Count, Avg
from django.db.models.functions import TruncYear
from django.http import JsonResponse
from django.shortcuts import render
from datetime import date, datetime as dt
import pandas as pd

from .models import Exam, Operator, Clinic


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
    years = list(set([obj.year for obj in exam_counts]))

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
        plot_data[str(obj.year)]['y'][anatomy_regions.index(obj.anatomy_region)] = obj.num_exams

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
