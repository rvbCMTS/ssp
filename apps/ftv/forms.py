from ckeditor.widgets import CKEditorWidget
import datetime
from dateutil.relativedelta import relativedelta
from django import forms
from tempus_dominus.widgets import DateTimePicker

from .models import Machine


class FtvOP300QAForm(forms.Form):
    modality = forms.ModelChoiceField(
        queryset=Machine.objects.all().filter(in_use__exact=True), label='Modalitet'
    )
    qa_date = forms.DateTimeField(
        label='Datum', input_formats=('%Y-%m-%d %H:%M:%S',),
        widget=DateTimePicker(
            options={
                'minDate': (datetime.date.today() - relativedelta(years=1)).strftime('%Y-%m-%d'),
                'useCurrent': True,
                'collapse': False,
            }
        )
    )
    comment = forms.CharField(max_length=4000, label='Kommentar')
    signature = forms.CharField(max_length=400, label='Signatur')
    modality_change = forms.BooleanField()
    calibration_run = forms.RadioSelect()
    # Cefalogram
    cef_pix = forms.BooleanField(label='Ceph Pix godkänd')
    cef_qc = forms.NullBooleanField(label='Cef QC')
    cef_qc_homogeneous = forms.NullBooleanField(label='Området jämnt bestrålat')
    cef_qc_low_contrast = forms.NullBooleanField(label='Lågkontrastobjekt synliga')
    cef_qc_round_ball = forms.NullBooleanField(label='Kulan är rund')
    # Panoramic
    pan_geom = forms.BooleanField(label='Adjustment panGeom OK')
    pan_geom_x_offset = forms.DecimalField(label='X-offset (mm)', max_digits=8, decimal_places=2, localize=True)
    pan_geom_y_offset = forms.DecimalField(label='Y-offset (mm)', max_digits=8, decimal_places=2, localize=True)
    pan_geom_n_offset = forms.DecimalField(label='N-offset (mm)', max_digits=8, decimal_places=2, localize=True)
    pan_geom_j_offset = forms.DecimalField(label='J-offset (mm)', max_digits=8, decimal_places=2, localize=True)
    pan_pix = forms.BooleanField(label='FFPan detector calibration OK')
    pan_pix_ctq = forms.DecimalField(label='CTQ', max_digits=8, decimal_places=2, localize=True)
    pan_pix_signal_level = forms.DecimalField(label='Signal level', max_digits=8, decimal_places=2, localize=True)
    pan_pix_dark_level = forms.DecimalField(label='Dark level', max_digits=8, decimal_places=2, localize=True)
    pan_qc = forms.NullBooleanField(label='Pan QC')
    pan_qc_homogeneous = forms.NullBooleanField(label='Området jämnt bestrålat')
    pan_qc_high_contrast = forms.DecimalField(label='Högkontrastupplösning', max_digits=2, decimal_places=1, localize=True)
    pan_qc_low_contrast = forms.NullBooleanField(label='Lågkontrastobjekt synliga')
    pan_qc_round_ball = forms.NullBooleanField(label='Kulan är rund')
    pan_qc_distance_white_rods_ball = forms.NullBooleanField(label='Kulan mitt mellan pinnarna')
    # CBCT
    cbct_geom = forms.BooleanField(label='Geometry calibration godkänd')
    cbct_geom_ctq = forms.DecimalField(label='CTQ', max_digits=8, decimal_places=2, localize=True)
    cbct_geom_scan_diff = forms.DecimalField(label='Scan diff (deg)', max_digits=8, decimal_places=2, localize=True)
    cbct_geom_n_offset = forms.DecimalField(label='N-offset (mm)', max_digits=8, decimal_places=2, localize=True)
    cbct_geom_x_offset = forms.DecimalField(label='X-offset (mm)', max_digits=8, decimal_places=2, localize=True)
    cbct_geom_y_offset = forms.DecimalField(label='Y-offset (mm)', max_digits=8, decimal_places=2, localize=True)
    cbct_geom_j_offset = forms.DecimalField(label='J-offset (mm)', max_digits=8, decimal_places=2, localize=True)
    cbct_pix = forms.BooleanField(label='CT detector calbibration godkänd')
    cbct_pix_ctq = forms.DecimalField(label='CTQ', max_digits=8, decimal_places=2, localize=True)
    cbct_pix_signal_level = forms.DecimalField(label='Signal level', max_digits=8, decimal_places=2, localize=True)
    cbct_pix_dark_level = forms.DecimalField(label='Dark level', max_digits=8, decimal_places=2, localize=True)
    cbct_qc = forms.NullBooleanField(label='Quality Check godkänd')
    cbct_qc_pmma_min_value = forms.IntegerField(label='PMMA minimum value')
    cbct_qc_pmma_max_value = forms.IntegerField(label='PMMA maximum value')
    cbct_qc_pmma_std_dev = forms.IntegerField(label='PMMA maximum std. dev.')
    cbct_qc_ptfe = forms.IntegerField(label='PTFE')
    cbct_qc_ptfe_std_dev = forms.IntegerField(label='PTFE std. dev.')
    cbct_qc_air = forms.IntegerField(label='AIR')
    cbct_qc_air_std_dev = forms.IntegerField(label='AIR std. dev.')
