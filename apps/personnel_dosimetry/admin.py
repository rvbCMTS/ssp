from django.contrib import admin
from .models import (Personnel, VendorDosimeterPlacement, DosimeterPlacement, DosimeterLaterality,
                     Clinic, ClinicDisplayName, Profession, Result, Deviation)


class PersonnelModelAdmin(admin.ModelAdmin):
    list_display = ['dosimetry_vendor_id', 'person_id', 'person_name', 'profession']
    list_display_links = ['dosimetry_vendor_id', 'person_id', 'person_name', 'profession']
    list_filter = ['profession']
    search_fields = ['dosimetry_vendor_id', 'person_id', 'person_name', 'profession']

    class Meta:
        model = Personnel


class ClinicDisplayNameModelAdmin(admin.ModelAdmin):
    list_display = ['display_name']
    list_display_links = ['display_name']
    list_filter = ['display_name']
    search_fields = ['display_name']

    class Meta:
        model = ClinicDisplayName


class ClinicModelAdmin(admin.ModelAdmin):
    list_display = ['clinic', 'display_name']
    list_display_links = ['clinic', 'display_name']
    list_filter = ['clinic', 'display_name']
    search_fields = ['clinic', 'display_name']

    class Meta:
        model = Clinic


class VendorDosimeterPlacementModelAdmin(admin.ModelAdmin):
    list_display = ['vendor_dosimeter_placement', 'dosimeter_placement', 'dosimeter_laterality']
    list_display_links = ['vendor_dosimeter_placement', 'dosimeter_placement', 'dosimeter_laterality']
    list_filter = ['vendor_dosimeter_placement', 'dosimeter_placement', 'dosimeter_laterality']
    search_fields = ['vendor_dosimeter_placement', 'dosimeter_placement', 'dosimeter_laterality']

    class Meta:
        model = VendorDosimeterPlacement


class DosimeterLateralityModelAdmin(admin.ModelAdmin):
    list_display = ['dosimeter_laterality']
    list_display_links = ['dosimeter_laterality']
    list_filter = ['dosimeter_laterality']
    search_fields = ['dosimeter_laterality']

    class Meta:
        model = DosimeterLaterality


class DosimeterPlacementModelAdmin(admin.ModelAdmin):
    list_display = ['dosimeter_placement']
    list_display_links = ['dosimeter_placement']
    list_filter = ['dosimeter_placement']
    search_fields = ['dosimeter_placement']

    class Meta:
        model = DosimeterPlacement


class ProfessionModelAdmin(admin.ModelAdmin):
    list_display = ['landauer_profession_id', 'profession']
    list_display_links = ['landauer_profession_id', 'profession']
    list_filter = ['profession']
    search_fields = ['landauer_profession_id', 'profession']

    class Meta:
        model = Profession


class ResultModelAdmin(admin.ModelAdmin):
    list_display = ['dosimetry_vendor', 'personnel', 'dosimeter_type', 'vendor_dosimetry_placement', 'clinic', 'report', 'measurement_period_start', 'measurement_period_stop', 'hp10', 'hp007', 'hp10tn', 'hp10fn', 'other_measure', 'production', 'production_isotope', 'yearly_production', 'deviation', 'spot_check', 'area_measurement']
    list_display_links = ['dosimetry_vendor', 'personnel', 'dosimeter_type', 'vendor_dosimetry_placement', 'clinic', 'report', 'measurement_period_start', 'measurement_period_stop', 'hp10', 'hp007', 'hp10tn', 'hp10fn', 'other_measure', 'production', 'production_isotope', 'yearly_production', 'deviation', 'spot_check', 'area_measurement']
    list_filter = ['dosimetry_vendor', 'dosimeter_type', 'vendor_dosimetry_placement', 'clinic', 'production_isotope', 'deviation', 'spot_check', 'area_measurement']
    search_fields = ['dosimetry_vendor', 'personnel', 'dosimeter_type', 'vendor_dosimetry_placement', 'clinic', 'report', 'measurement_period_start', 'measurement_period_stop', 'hp10', 'hp007', 'hp10tn', 'hp10fn', 'other_measure', 'production', 'production_isotope', 'yearly_production', 'deviation', 'spot_check', 'area_measurement']

    class Meta:
        model = Result


class DeviationModelAdmin(admin.ModelAdmin):
    list_display = ['result', 'reported_to_authority', 'comment']
    list_display_links = ['result', 'reported_to_authority', 'comment']
    list_filter = ['reported_to_authority']
    search_fields = ['comment']

    class Meta:
        model = Deviation


admin.site.register(Personnel, PersonnelModelAdmin)
admin.site.register(Clinic, ClinicModelAdmin)
admin.site.register(ClinicDisplayName, ClinicDisplayNameModelAdmin)
admin.site.register(VendorDosimeterPlacement, VendorDosimeterPlacementModelAdmin)
admin.site.register(DosimeterPlacement, DosimeterPlacementModelAdmin)
admin.site.register(DosimeterLaterality, DosimeterLateralityModelAdmin)
admin.site.register(Profession, ProfessionModelAdmin)
admin.site.register(Result, ResultModelAdmin)
admin.site.register(Deviation, DeviationModelAdmin)
