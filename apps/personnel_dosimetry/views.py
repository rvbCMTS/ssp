from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.db.models.functions import TruncYear
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseServerError
import json
from math import ceil
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .forms import FullBodyMeasurementForm, PersonnelForm
from .functions import (import_personnel_dosimetry_report, get_personnel_dosimetry_filter_data, get_plot_and_table_data,
                        format_plot_and_table_data)
from .models import Clinic, Result, FullBodyDosimetry, FULL_BODY_ASSESSMENT, Personnel
from .serializers import PersonnelDosimetryResultSerializer
from .helpers import (_add_time_filter, _add_clinic_filter, _add_dosimeter_placement_filter, _add_personnel_filter,
                      _add_profession_filter, RequestParameterValues)


def personnel_dosimetry_results(request):
    try:
        context = get_personnel_dosimetry_filter_data(user=request.user,
                                                      time_period_start=(dt.now() - relativedelta(years=1)))
    except:
        return HttpResponseServerError()

    return render(request=request, template_name='personnel_dosimetry/DosimetryResults.html',
                  context=context)


def full_body_dosimetry_view(request):
    if request.method == 'POST':
        form = FullBodyMeasurementForm(request.POST)
        if form.is_valid():
            try:
                fbm = FullBodyDosimetry(
                    personnel=form.cleaned_data.get('personnel'),
                    measurement_date=form.cleaned_data.get('measurement_date'),
                    result=form.cleaned_data.get('result'),
                    comment=form.cleaned_data.get('comment'),
                )
                fbm.save()
                messages.success(request=request,
                                 message=f'Mätning sparad för {form.cleaned_data.get("personnel").person_name}')
            except Exception as e:
                messages.error(request=request,
                               message='Kunde inte spara mätningen')

    form = FullBodyMeasurementForm()
    measurement_result = FullBodyDosimetry.objects.all().prefetch_related('personnel')
    if measurement_result is not None:
        result_types = dict(FULL_BODY_ASSESSMENT)
        table_data = [
            [obj.measurement_date.strftime('%Y-%m-%d %H:%M:%S'), obj.personnel.person_name, result_types.get(obj.result), obj.comment]
            for obj in measurement_result]
    else:
        table_data = []

    return render(request=request, template_name='personnel_dosimetry/FullBodyDosimetry.html',
                  context={'table_data': json.dumps(table_data), 'form': form})


def new_personnel_form(request):
    if request.method == 'POST':
        form = PersonnelForm(request.POST)
        if form.is_valid():
            try:
                personnel = Personnel(
                    person_id=form.cleaned_data.get('person_id'),
                    person_name=form.cleaned_data.get('person_name'),
                    profession=form.cleaned_data.get('profession')
                )
                personnel.save()
                messages.success(request=request,
                                 message='Ny personal sparad i databasen')
            except Exception as e:
                messages.error(request=request, message='Kunde inte spara personalen')

    form = PersonnelForm()
    return render(request=request, template_name='personnel_dosimetry/NewPersonnel.html', context={'form': form})


def api_parse_new_landauer_reports(request):
    test = import_personnel_dosimetry_report(
        vendor='Landauer',
        input_file_directory=settings.PERSONNEL_DOSIMETRY_DIRS['Landauer']['incoming'],
        output_file_directory=settings.PERSONNEL_DOSIMETRY_DIRS['Landauer']['outgoing']
    )

    return redirect('pd:pd-result')


class PersonnelDosimetryResultList(APIView):
    """
    List all personnel dosimetry results
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        params = RequestParameterValues(request=request)

        data = get_plot_and_table_data(
            user=request.user, time_interval=params.TimeInterval, clinic=params.Clinic, profession=params.Profession,
            personnel=params.Personnel, dosimeter_placement=params.DosimeterPlacement,
            exclude_spot_check=params.SpotCheck, exclude_area_measurement=params.AreaMeasurement)

        output = format_plot_and_table_data(data=data)

        return Response(output)


class FilterList(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        time_interval = self.request.query_params.get('timeInterval', None)
        if time_interval is not None:
            time_interval = int(time_interval)
        clinic = self.request.query_params.get('clinic', None)
        profession_filter = self.request.query_params.get('profession', None)
        personnel_filter = self.request.query_params.get('personnel', None)
        triggering_element = self.request.query_params.get('triggeringElement', None)

        output = []

        if triggering_element in ['idTime']:
            # Get a list of the clinics
            clinics = Result.objects.all()
            clinics = _add_time_filter(databaseobject=clinics, time_interval=time_interval)
            clinics = clinics.values('clinic__display_name_id', 'clinic__display_name__display_name').distinct()
            clinics = [{'id': obj['clinic__display_name_id'], 'name': obj['clinic__display_name__display_name']} for obj in clinics]
            clinics.append({'id': 'all', 'name': 'Alla'})
            clinics.insert(0, {'id': 'null', 'name': 'Välj klinik'})

            output.append({'id': '#idClinic', 'choices': clinics, 'selectedValue': 'null'})

        if triggering_element in ['idTime', 'idClinic']:
            # Get a list of professions for users present for the selected time interval and clinic
            professions = Result.objects.all()
            professions = _add_time_filter(databaseobject=professions, time_interval=time_interval)
            if triggering_element not in ['idTime']:
                professions = _add_clinic_filter(databaseobject=professions, clinic=clinic)
            professions = professions.values('personnel__profession__profession', 'personnel__profession_id').order_by(
                'personnel__profession__profession').distinct()
            professions = [{'id': obj['personnel__profession_id'], 'name': obj['personnel__profession__profession']} for
                          obj in professions]
            professions.insert(0, {'id': 'all', 'name': 'Alla'})

            output.append({'id': '#idPersonnelCategory', 'choices': professions, 'selectedValue': 'all'})

        if triggering_element in ['idTime', 'idClinic', 'idPersonnelCategory']:
            # Get a list of personnel for users present for the selected time interval, clinic, and professiln
            personnel = Result.objects.all()
            personnel = _add_time_filter(databaseobject=personnel, time_interval=time_interval)
            if triggering_element not in ['idTime']:
                personnel = _add_clinic_filter(databaseobject=personnel, clinic=clinic)
                if triggering_element not in ['idTime', 'idClinic']:
                    personnel = _add_profession_filter(databaseobject=personnel, profession=profession_filter)
            personnel = personnel.values('personnel_id', 'personnel__person_name')
            if request.user.has_perm('personnel_dosimetry.view_personnel_names'):
                personnel = [{'id': obj['personnel_id'], 'name': obj['personnel__person_name']} for obj in
                             personnel.order_by('personnel__person_name').distinct()]
            else:
                personnel = [{'id': obj['personnel_id'], 'name': obj['personnel_id']} for obj in
                             personnel.order_by('personnel_id').distinct()]
            personnel.insert(0, {'id': 0, 'name': 'Alla'})

            output.append({'id': '#idPersonnel', 'choices': personnel, 'selectedValue': 0})

        if triggering_element in ['idTime', 'idClinic', 'idPersonnelCategory', 'idPersonnel']:
            # Get a list of dosimeter placements for users present for the selected time interval, clinic, profession,
            # and personnel
            dps = Result.objects.all()
            dps = _add_time_filter(databaseobject=dps, time_interval=time_interval)
            if triggering_element not in ['idTime']:
                dps = _add_clinic_filter(databaseobject=dps, clinic=clinic)
                if triggering_element not in ['idTime', 'idClinic']:
                    dps = _add_profession_filter(databaseobject=dps, profession=profession_filter)
                    if triggering_element not in ['idTime', 'idClinic', 'idPersonnelCategory']:
                        dps = _add_personnel_filter(databaseobject=dps, personnel=personnel_filter)
            dps = dps.values(
                'vendor_dosimetry_placement__dosimeter_placement__dosimeter_placement',
                'vendor_dosimetry_placement__dosimeter_placement_id'
            ).order_by(
                'vendor_dosimetry_placement__dosimeter_placement__dosimeter_placement'
            ).distinct()
            dps = [{'id': obj['vendor_dosimetry_placement__dosimeter_placement_id'],
                    'name': obj['vendor_dosimetry_placement__dosimeter_placement__dosimeter_placement']} for obj in
                   dps]
            dps.insert(0, {'id': 0, 'name': 'Alla'})
            output.append({'id': '#idDosimeterPlacement', 'choices': dps, 'selectedValue': 0})

        return Response(output)
