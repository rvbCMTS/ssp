from ckeditor.widgets import CKEditorWidget
from django import forms
from django.utils import timezone
from tempus_dominus.widgets import DateTimePicker

from .models import Clinic, ShieldingClassification


class RoomForm(forms.Form):
    clinic = forms.ModelChoiceField(queryset=Clinic.objects.all(), label='Klinik', empty_label='Välj klinik')
    room = forms.CharField(max_length=200, required=True, label='Rumsbeteckning')
    roomWidth = forms.FloatField(required=False, label='Rumsbredd')
    roomLength = forms.FloatField(required=False, label='Rumslängd')
    modalityType = forms.CharField(max_length=100, required=False, label='Modalitetstyp/-er i rummet')
    shielding = forms.CharField(widget=CKEditorWidget(), label='Strålskärmningsbeskrivning')
    shieldingClassification = forms.ModelChoiceField(queryset=ShieldingClassification.objects.all(),
                                                     label='Klassificering')
    shieldingClassificationDate = forms.DateTimeField(
        label='Klassificeringsdatum', input_formats=('%Y-%m-%d %H:%M:%S',),
        widget=DateTimePicker(options={'useCurrent': True, 'collapse': False},),
        initial=timezone.now(), required=False)
    shieldingClassificationSignature = forms.CharField(max_length=400, required=False, label='Klassificeringssignatur')
    shieldingClassificationComment = forms.CharField(label='Klassificeringskommentar')
    drawing = forms.CharField(max_length=4000, label='Sökväg till ritning', required=False)
