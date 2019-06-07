from django import forms
from django.utils import timezone
from tempus_dominus.widgets import DatePicker

from .models import Exam, AnatomyRegion, Clinic, ClinicCategory, Modality, Operator, OperatorClinicMap, ModalityClinicMap, DOSE_UNITS


class FluoroTimeForm(forms.Form):
    clinic = forms.ModelChoiceField(queryset=Clinic.objects.all().prefetch_related('hospital'), label='Klinik', required=True)
    anatomical_region = forms.ModelChoiceField(queryset=AnatomyRegion.objects.all(), label='Anatomiskt område', required=True)
    modality = forms.ModelChoiceField(queryset=Modality.objects.all().filter(active=True), label='Modalitet', required=True)
    operator = forms.ModelChoiceField(queryset=Operator.objects.all(), label='Operator', required=True)
    exam_date = forms.DateField(label='Undersökningsdatum', input_formats=('%Y-%m-%d',),
                                widget=DatePicker(
                                    options={'useCurrent': True, 'collapse': False},
                                ), initial=timezone.now(), required=True)
    pediatric = forms.ChoiceField(choices=((1, 'Vuxen'), (2, 'Barn')),
                                  widget=forms.RadioSelect, label='Vuxen/Barn', initial=1, required=True)
    exam_id = forms.CharField(max_length=400, label='Undersökningsnummer', required=True)
    fluoro_time_minutes = forms.IntegerField(min_value=0, label='Minuter', required=True)
    fluoro_time_seconds = forms.IntegerField(min_value=0, max_value=59, label='Sekunder', required=True)
    fluoro_dose = forms.FloatField(min_value=0, label='Dos (DAP)', required=True)
    fluoro_dose_unit = forms.ChoiceField(choices=DOSE_UNITS, label='Dosenhet', required=True)
