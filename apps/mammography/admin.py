from django import forms
from django.contrib import admin
from .models import Modality, Reference, Measurement, RoiValue, MeasurementParameter
from ckeditor.widgets import CKEditorWidget


class ModalityAdminForm(forms.ModelForm):
    instructions = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Modality
        fields = '__all__'


class ModalityModelAdmin(admin.ModelAdmin):
    list_display = ['location', 'room', 'display_name', 'inventory_system_number', 'manufacturer', 'manufacturer_model',
                    'in_use', 'number_of_rois']
    list_display_links = ['location', 'room', 'display_name', 'inventory_system_number', 'manufacturer',
                          'manufacturer_model', 'in_use', 'number_of_rois']
    list_filter = ['manufacturer', 'manufacturer_model', 'in_use', 'location']
    search_fields = ['location', 'room', 'display_name', 'inventory_system_number',
                     'manufacturer', 'manufacturer_model']
    form = ModalityAdminForm

    class Meta:
        model = Modality


class MeasurementParameterModelAdmin(admin.ModelAdmin):
    list_display = ['modality', 'parameter', 'active']
    list_display_links = ['modality', 'parameter', 'active']
    list_filter = ['active', 'parameter', 'modality']
    search_fields = ['modality', 'parameter', 'active']

    class Meta:
        model = MeasurementParameter


class ReferenceModelAdmin(admin.ModelAdmin):
    list_display = ['parameter', 'parameter_value','tolerance', 'tolerance_unit',  'set_date', 'active']
    list_display_links = ['parameter', 'parameter_value', 'tolerance', 'tolerance_unit',  'set_date', 'active']
    list_filter = ['active', 'parameter']
    search_fields = ['parameter', 'parameter_value','tolerance', 'tolerance_unit',  'set_date', 'active']

    class Meta:
        model: Reference


class MeasurementModelAdmin(admin.ModelAdmin):
    list_display = ['modality', 'measurement_date', 'mas', 'entrance_dose', 'comment', 'signature']
    list_display_links = ['modality', 'measurement_date', 'mas', 'entrance_dose', 'comment', 'signature']
    list_filter = ['modality', 'signature']
    search_fields = ['modality', 'measurement_date', 'mas', 'entrance_dose', 'comment', 'signature']

    class Meta:
        model: Measurement


class RoiValueModelAdmin(admin.ModelAdmin):
    list_display = ['measurement', 'roi', 'mean', 'stdev', 'signal_noise_ratio']
    list_display_links = ['measurement', 'roi', 'mean', 'stdev', 'signal_noise_ratio']
    search_fields = ['measurement', 'roi', 'mean', 'stdev', 'signal_noise_ratio']

    class Meta:
        model: RoiValue


admin.site.register(Modality, ModalityModelAdmin)
admin.site.register(MeasurementParameter, MeasurementParameterModelAdmin)
admin.site.register(Reference, ReferenceModelAdmin)
admin.site.register(Measurement, MeasurementModelAdmin)
admin.site.register(RoiValue, RoiValueModelAdmin)
