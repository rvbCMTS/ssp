from django import forms
from django.utils import timezone
from tempus_dominus.widgets import DateTimePicker

from .models import Personnel, FullBodyDosimetry, FULL_BODY_ASSESSMENT, Profession


class FullBodyMeasurementForm(forms.Form):
    personnel = forms.ModelChoiceField(queryset=Personnel.objects.filter(person_id__isnull=False).all(), label='Personal', required=True)
    measurement_date = forms.DateTimeField(
        label='Mätdatum', input_formats=('%Y-%m-%d %H:%M:%S',),
        widget=DateTimePicker(
            options={'useCurrent': True, 'collapse': False},
        ), initial=timezone.now(), required=True)
    result = forms.ChoiceField(choices=FULL_BODY_ASSESSMENT, label='Resultat', required=True)
    comment = forms.CharField(max_length=4000, label='Kommentar', required=False)


class PersonnelForm(forms.Form):
    person_id = forms.CharField(label='Personnummer', max_length=400, required=True)
    person_name = forms.CharField(label='Namn', max_length=400, required=True)
    profession = forms.ModelChoiceField(label='Yrkeskategori', queryset=Profession.objects.all(), required=True)
