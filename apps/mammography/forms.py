import datetime
from dateutil.relativedelta import relativedelta
from django import forms
from tempus_dominus.widgets import DateTimePicker

from .models import Modality


class MammographyWeeklyQAForm(forms.Form):
    modality = forms.ModelChoiceField(
        queryset=Modality.objects.all().filter(in_use__exact=True), label='Modalitet')
    measurement_date = forms.DateTimeField(
        label='Mätdatum', input_formats=('%Y-%m-%d %H:%M:%S',),
        widget=DateTimePicker(
            options={
                'minDate': (datetime.date.today() - relativedelta(years=1)).strftime('%Y-%m-%d'),
                'useCurrent': True,
                'collapse': False,
            }
        ))
    mas = forms.FloatField(label='mAs', min_value=0, widget=forms.NumberInput(attrs={'class': 'validate-field'}))
    entrance_dose = forms.FloatField(label='Ingångsdos', min_value=0,
                                     widget=forms.NumberInput(attrs={'class': 'validate-field'}))
    comment = forms.CharField(required=False, max_length=4000, label='Kommentar',
                              widget=forms.TextInput(attrs={'class': 'full-width-form-field'}))
    signature = forms.CharField(max_length=200, label='Signatur')


class ROIForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if 'rois' in kwargs:
            number_of_rois = kwargs.pop('rois')
            number_of_rois = int(number_of_rois)
            super(ROIForm, self).__init__(*args, **kwargs)

            for i in range(number_of_rois):
                self.fields[f'{i+1}_mean'] = forms.FloatField(label='Medelvärde')
                self.fields[f'{i+1}_stdev'] = forms.FloatField(label='Stdev')
                self.fields[f'{i+1}_snr'] = forms.FloatField(label='SNR')

    def roi_values(self):
        for name, value in self.cleaned_data:
            yield (name, value)
