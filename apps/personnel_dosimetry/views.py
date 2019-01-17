from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models.functions import TruncYear
from django.shortcuts import render, redirect
from django.http import Http404
from math import ceil
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .functions import import_personnel_dosimetry_report
from .models import Clinic, Result
from .serializers import PersonnelDosimetryResultSerializer


def personnel_dosimatery_results(request):
    # Get a reversed list of years with dosimetry data
    years = Result.objects.annotate(year=TruncYear('measurement_period_center')).order_by('-year').values(
        'year').distinct()
    years = [obj['year'].year for obj in years]

    # Get a list of the clinics active during the last 12 months
    clinics = Result.objects.filter(measurement_period_center__gte=(dt.now() - relativedelta(years=1))).values(
        'clinic__id'
    )
    clinic_ids = [obj['clinic__id'] for obj in clinics]

    clinics = Clinic.objects.order_by('display_clinic', 'clinic').all()
    clinics = [{'id': obj.pk, 'name': obj.display_clinic} for obj in clinics if obj.pk in clinic_ids]

    # Get a list of professions for users present in the database
    profession = Result.objects.all().filter(measurement_period_center__gte=(dt.now() - relativedelta(years=1))).values(
        'personnel__profession__profession', 'personnel__profession_id').order_by(
        'personnel__profession__profession').distinct()
    profession = [{'id': obj['personnel__profession_id'], 'name': obj['personnel__profession__profession']} for obj in
                  profession]

    # Get a list of personnel

    personnel = Result.objects.all().filter(measurement_period_center__gte=(dt.now() - relativedelta(years=1))).values(
        'personnel_id', 'personnel__person_name')

    if request.user.has_perm('personnel_dosimetry.view_personnel_names'):
        personnel = [{'id': obj['personnel_id'], 'name': obj['personnel__person_name']} for obj in personnel.order_by('personnel__person_name').distinct()]
    else:
        personnel = [{'id': obj['personnel_id'], 'name': obj['personnel_id']} for obj in personnel.order_by('personnel_id').distinct()]

    # Get a list of dosimeter placements
    dp = Result.objects.all().filter(measurement_period_center__gte=(dt.now() - relativedelta(years=1))).values(
        'vendor_dosimetry_placement__dosimeter_placement__dosimeter_placement',
        'vendor_dosimetry_placement__dosimeter_placement_id'
    ).order_by('vendor_dosimetry_placement__dosimeter_placement__dosimeter_placement').distinct()
    dp = [{'id': obj['vendor_dosimetry_placement__dosimeter_placement_id'],
           'placement': obj['vendor_dosimetry_placement__dosimeter_placement__dosimeter_placement']} for obj in dp]
    
    return render(request=request, template_name='personnel_dosimetry/DosimetryResults.html',
                  context={
                      'filter_years': years,
                      'clinic': clinics,
                      'personnel_category': profession,
                      'personnel': personnel,
                      'dosimeter_placement': dp
                  })


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
        time_interval = self.request.query_params.get('timeInterval', None)
        if time_interval is not None:
            time_interval = int(time_interval)
        clinic = self.request.query_params.get('clinic', None)
        profession = self.request.query_params.get('profession', None)
        personnel =self.request.query_params.get('personnel', None)
        dosimeter_placement = self.request.query_params.get('dosimeterPlacement', None)
        spotcheck = self.request.query_params.get('spotcheck', None)
        area_measurement = self.request.query_params.get('areameasurement', None)

        layout2 = {
            'displayModeBar': False,
            'displaylogo': False
        }

        results = Result.objects.all()
        # Add time interval filtering (time_interval == 0: last 12 months, time_interval == 1: no time filtering)
        if time_interval is not None and int(time_interval) > 1:
            results = results.filter(measurement_period_center__year=int(time_interval))
        elif time_interval < 1:
            # Get only values from the last 12 months
            results = results.filter(measurement_period_center__gte=(dt.now() - relativedelta(years=1)))

        # Add clinic filter
        if clinic is not None and clinic not in ['all', 'null'] and int(clinic) > 0:
            results = results.filter(clinic_id__exact=int(clinic))
        else:
            return Response({
                'plotData': [
                    {
                        'id': 'hp10Plot',
                        'data': [],
                        'layout': {
                            'xaxis': {
                                'title': 'Datum'
                            },
                            'yaxis': {
                                'title': 'Hp(10) [mSv]',
                                'range': [-0.05, 1.0]
                            },
                            'title': 'Hp(10)',
                            'showlegend': False,
                            'hoverinfo': 'y+name'
                        },
                        'layout2': layout2
                    },
                    {
                        'id': 'hp007Plot',
                        'data': [],
                        'layout': {
                            'xaxis': {
                                'title': 'Datum'
                            },
                            'yaxis': {
                                'title': 'Hp(0,07) [mSv]',
                                'range': [-0.05, 1.0]
                            },
                            'title': 'Hp(0,07)',
                            'showlegend': False
                        },
                        'layout2': layout2
                    },
                    {
                        'id': 'hp10tnPlot',
                        'data': [],
                        'layout': {
                            'xaxis': {
                                'title': 'Datum'
                            },
                            'yaxis': {
                                'title': 'Hp(10)tn [mSv]',
                                'range': [-0.05, 1.0]
                            },
                            'title': 'Hp(10) Termiska neutroner',
                            'showlegend': False
                        },
                        'layout2': layout2
                    },
                    {
                        'id': 'hp10fnPlot',
                        'data': [],
                        'layout': {
                            'xaxis': {
                                'title': 'Datum'
                            },
                            'yaxis': {
                                'title': 'Hp(10)fn [mSv]',
                                'range': [-0.05, 1.0]
                            },
                            'title': 'Hp(10) Snabba neutroner',
                            'showlegend': False
                        },
                        'layout2': layout2
                    }
                ],
                'tableData': {
                    'data': []
                }
            })

        # Add profession filter
        if profession is not None and profession != 'all' and int(profession) > 0:
            results = results.filter(personnel__profession_id__exact=int(profession))

        # Add personnel filter
        if personnel is not None and personnel != 'all' and int(personnel) > 0:
            results = results.filter(personnel_id__exact=int(personnel))

        # Add dosimeter placement filter
        if dosimeter_placement is not None and dosimeter_placement != 'all' and int(dosimeter_placement) > 0:
            results = results.filter(vendor_dosimetry_placement__dosimeter_placement_id__exact=int(dosimeter_placement))

        if spotcheck is None or not int(spotcheck) == 0:
            results = results.filter(spot_check=False)

        if area_measurement is None or int(area_measurement) == 0:
            results = results.filter(area_measurement=False)

        plot_data = {}
        table_data = {}
        for obj in results:
            #ind = obj.personnel_id
            if obj.vendor_dosimetry_placement.dosimeter_placement is not None:
                dosimeter_placement = obj.vendor_dosimetry_placement.dosimeter_placement.dosimeter_placement
            else:
                dosimeter_placement = obj.vendor_dosimetry_placement.vendor_dosimeter_placement

            if obj.vendor_dosimetry_placement.dosimeter_laterality is not None:
                dosimeter_laterality = obj.vendor_dosimetry_placement.dosimeter_laterality.dosimeter_laterality
            else:
                dosimeter_laterality = 'Sida okänd'

            if request.user.has_perm('personnel_dosimetry.view_personnel_names'):
                ind = f'{obj.personnel.person_name} ({dosimeter_placement}, {dosimeter_laterality})'
            else:
                ind = f'{obj.personnel_id} ({dosimeter_placement}, {dosimeter_laterality})'

            if ind not in plot_data.keys():
                plot_data[ind] = {
                    'hp10': {
                        'x': [],
                        'y': [],
                        'name': str(),
                        'mode': 'markers',
                        'type': 'scatter',
                        'text': [],
                        'hoverinfo': 'y+text'
                    },
                    'hp007': {
                        'x': [],
                        'y': [],
                        'name': str(),
                        'mode': 'markers',
                        'type': 'scatter',
                        'text': [],
                        'hoverinfo': 'y+text'
                    },
                    'hp10tn': {
                        'x': [],
                        'y': [],
                        'name': str(),
                        'mode': 'markers',
                        'text': [],
                        'type': 'scatter',
                        'hoverinfo': 'y+text'
                    },
                    'hp10fn': {
                        'x': [],
                        'y': [],
                        'name': str(),
                        'mode': 'markers',
                        'text': [],
                        'type': 'scatter',
                        'hoverinfo': 'y+text'
                    }
                }

            plot_data[ind]['hp10']['x'].append(obj.measurement_period_center)
            plot_data[ind]['hp10']['y'].append(obj.hp10)
            plot_data[ind]['hp10']['name'] = ind
            plot_data[ind]['hp10']['text'].append(ind)
            plot_data[ind]['hp007']['x'].append(obj.measurement_period_center)
            plot_data[ind]['hp007']['y'].append(obj.hp007)
            plot_data[ind]['hp007']['name'] = ind
            plot_data[ind]['hp007']['text'].append(ind)
            plot_data[ind]['hp10tn']['x'].append(obj.measurement_period_center)
            plot_data[ind]['hp10tn']['y'].append(obj.hp10tn)
            plot_data[ind]['hp10tn']['name'] = ind
            plot_data[ind]['hp10tn']['text'].append(ind)
            plot_data[ind]['hp10fn']['x'].append(obj.measurement_period_center)
            plot_data[ind]['hp10fn']['y'].append(obj.hp10fn)
            plot_data[ind]['hp10fn']['name'] = ind
            plot_data[ind]['hp10fn']['text'].append(ind)

            table_data.setdefault(ind, {'hp10': [], 'hp007': [], 'hp10tn': [], 'hp10fn': []})
            table_data[ind]['hp10'].append(obj.hp10)
            table_data[ind]['hp007'].append(obj.hp007)
            table_data[ind]['hp10tn'].append(obj.hp10tn)
            table_data[ind]['hp10fn'].append(obj.hp10fn)

        hp10max = 0
        hp10data = []
        hp007data = []
        hp007max = 0
        hp10tndata = []
        hp10tnmax = 0
        hp10fndata = []
        hp10fnmax = 0
        for _, obj in plot_data.items():
            hp10max = max(filter(lambda x: x!=None, [hp10max, max(filter(lambda x: x!=None, [0] + obj['hp10']['y']))]))
            hp10data += [obj['hp10']]
            hp007max = max(filter(lambda x: x!=None, [hp007max, max(filter(lambda x: x!=None, [0] + obj['hp007']['y']))]))
            hp007data.append(obj['hp007'])
            hp10tnmax = max(filter(lambda x: x!=None, [hp10tnmax, max(filter(lambda x: x!=None, [0] + obj['hp10tn']['y']))]))
            hp10tndata.append(obj['hp10tn'])
            hp10fnmax = max(filter(lambda x: x!=None, [hp10fnmax, max(filter(lambda x: x!=None, [0] + obj['hp10fn']['y']))]))
            hp10fndata.append(obj['hp10fn'])

        output = {
            'plotData': [
                {
                    'id': 'hp10Plot',
                    'data': hp10data,
                    'layout': {
                        'xaxis': {
                            'title': 'Datum',
                            'tickformat': '%b-%y'
                        },
                        'yaxis': {
                            'title': 'Hp(10) [mSv]',
                            'range': [-0.05, (1.0 if hp10max < 1.0 else ceil(hp10max))]
                        },
                        'title': 'Hp(10)',
                        'showlegend': False,
                        'hovermode': 'closest'
                    },
                    'layout2': layout2
                },
                {
                    'id': 'hp007Plot',
                    'data': hp007data,
                    'layout': {
                        'xaxis': {
                            'title': 'Datum',
                            'tickformat': '%b-%y'
                        },
                        'yaxis': {
                            'title': 'Hp(0,07) [mSv]',
                            'range': [-0.05, (1.0 if hp007max < 1.0 else ceil(hp007max))]
                        },
                        'title': 'Hp(0,07)',
                        'showlegend': False,
                        'hoverinfo': 'y+name',
                        'hovermode': 'closest'
                    },
                    'layout2': layout2
                },
                {
                    'id': 'hp10tnPlot',
                    'data': hp10tndata,
                    'layout': {
                        'xaxis': {
                            'title': 'Datum',
                            'tickformat': '%b-%y'
                        },
                        'yaxis': {
                            'title': 'Hp(10)tn [mSv]',
                            'range': [-0.05, (1.0 if hp10tnmax < 1.0 else ceil(hp10tnmax))]
                        },
                        'title': 'Hp(10) Termiska neutroner',
                        'showlegend': False,
                        'hovermode': 'closest'
                    },
                    'layout2': layout2
                },
                {
                    'id': 'hp10fnPlot',
                    'data': hp10fndata,
                    'layout': {
                        'xaxis': {
                            'title': 'Datum',
                            'tickformat': '%b-%y'
                        },
                        'yaxis': {
                            'title': 'Hp(10)fn [mSv]',
                            'range': [-0.05, (1.0 if hp10fnmax < 1.0 else ceil(hp10fnmax))]
                        },
                        'title': 'Hp(10) Snabba neutroner',
                        'showlegend': False,
                        'hovermode': 'closest'
                    },
                    'layout2': layout2
                }
            ],
            'tableData': {
                'data': [[
                    str(ind),
                    f"{sum(filter(lambda x: x!=None, obj['hp10'])):.2f}",
                    f"{sum(filter(lambda x: x!=None, obj['hp007'])):.2f}",
                    f"{sum(filter(lambda x: x!=None, obj['hp10tn'])):.2f}",
                    f"{sum(filter(lambda x: x!=None, obj['hp10fn'])):.2f}"
                ] for ind, obj in table_data.items()]
            }
        }

        # serializer = PersonnelDosimetryResultSerializer(results, many=True)
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
            clinics = clinics.values('clinic_id', 'clinic__display_clinic').distinct()
            clinics = [{'id': obj['clinic_id'], 'name': obj['clinic__display_clinic']} for obj in clinics]
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


# Helper functions
def _add_time_filter(databaseobject, time_interval: int=None):
    if time_interval is None or time_interval == 0:
        return databaseobject.filter(measurement_period_center__gte=(dt.now() - relativedelta(years=1)))
    elif time_interval > 1:
        return databaseobject.filter(measurement_period_center__year=time_interval)
    else:
        return databaseobject


def _add_clinic_filter(databaseobject, clinic):
    if clinic is not None:
        if isinstance(clinic, int) and clinic > 0:
            return databaseobject.filter(clinic_id__exact=clinic)
        else:
            try:
                clinic = int(clinic)
            except:
                return databaseobject
            if clinic > 0:
                return databaseobject.filter(clinic_id__exact=clinic)

    return databaseobject


def _add_profession_filter(databaseobject, profession):
    if profession is not None:
        if isinstance(profession, int) and profession > 0:
            return databaseobject.filter(personnel__profession_id__exact=profession)
        else:
            try:
                profession = int(profession)
            except:
                return databaseobject
            if profession > 0:
                return databaseobject.filter(personnel__profession_id__exact=profession)

    return databaseobject


def _add_personnel_filter(databaseobject, personnel):
    if personnel is not None:
        if isinstance(personnel, int) and personnel > 0:
            return databaseobject.filter(personnel_id__exact=personnel)
        else:
            try:
                personnel = int(personnel)
            except:
                return databaseobject
            if personnel > 0:
                return databaseobject.filter(personnel_id__exact=personnel)

    return databaseobject


def _add_dosimeter_placement_filter(databaseobject, dosimeter_placement):
    if dosimeter_placement is not None:
        if isinstance(dosimeter_placement, int) and dosimeter_placement > 0:
            return databaseobject.filter(vendor_dosimetry_placement__dosimeter_placement_id__exact=dosimeter_placement)
        else:
            try:
                dosimeter_placement = int(dosimeter_placement)
            except:
                return databaseobject
            if dosimeter_placement > 0:
                return databaseobject.filter(
                    vendor_dosimetry_placement__dosimeter_placement_id__exact=dosimeter_placement)

    return databaseobject
