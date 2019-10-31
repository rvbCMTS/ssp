from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from typing import Optional


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
            return databaseobject.filter(clinic__display_name_id__exact=clinic)
        else:
            try:
                clinic = int(clinic)
            except:
                return databaseobject
            if clinic > 0:
                return databaseobject.filter(clinic__display_name_id__exact=clinic)

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


class RequestParameterValues:
    def __init__(self, request):
        time_interval = request.query_params.get('timeInterval', None)
        if time_interval is not None:
            time_interval = int(time_interval)
        else:
            time_interval = 0

        clinic = request.query_params.get('clinic', None)
        if clinic == 'null':
            clinic = 0
        if isinstance(clinic, str) and clinic == 'all':
            clinic = 0
        else:
            clinic = int(clinic)

        profession = request.query_params.get('profession', 0)
        if isinstance(profession, str) and profession == 'all':
            profession = 0
        else:
            profession = int(profession)

        personnel = request.query_params.get('personnel', 0)
        if isinstance(personnel, str) and personnel == 'all':
            personnel = 0
        else:
            personnel = int(personnel)

        dosimeter_placement = request.query_params.get('dosimeterPlacement', 0)
        if isinstance(dosimeter_placement, str) and dosimeter_placement == 'all':
            dosimeter_placement = 0
        else:
            dosimeter_placement = int(dosimeter_placement)
        spotcheck = int(request.query_params.get('spotcheck', 0))
        area_measurement = int(request.query_params.get('areameasurement', 0))

        self.TimeInterval: int = time_interval
        self.Clinic: Optional[int] = clinic
        self.Profession: int = profession
        self.Personnel: int = personnel
        self.DosimeterPlacement: int = dosimeter_placement
        self.SpotCheck: bool = spotcheck < 1
        self.AreaMeasurement: bool = area_measurement < 1
