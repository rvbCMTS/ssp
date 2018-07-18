from django.contrib import admin
from .models import Exam, ExamDescription, Modality, DirtyModality, DirtyOperator, DirtyClinic, Clinic, Operator,\
    ModalityClinicMap, OperatorClinicMap, Updates, AnatomyRegion, ClinicCategory, Hospital


class HospitalModelAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    list_filter = []

    class Meta:
        model = Hospital


class ClinicModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital', 'clinic_category']
    list_display_links = ['name', 'hospital', 'clinic_category']
    list_filter = ['clinic_category']

    class Meta:
        model = Clinic


class ClinicCategoryModelAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']

    class Meta:
        model = ClinicCategory


class DirtyClinicModelAdmin(admin.ModelAdmin):
    list_display = ['dirty_name', 'clinic']
    list_display_links = ['dirty_name', 'clinic']
    list_filter = ['clinic']

    class Meta:
        model = DirtyClinic


class OperatorModelAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'clinic']
    list_display_links = ['first_name', 'last_name', 'clinic']

    class Meta:
        model = Operator


class DirtyOperatorModelAdmin(admin.ModelAdmin):
    list_display = ['dirty_name', 'operator']
    list_display_links = ['dirty_name', 'operator']

    class Meta:
        model = DirtyOperator


class ModalityModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'dose_unit', 'active']
    list_display_links = ['name', 'dose_unit', 'active']
    list_filter = ['active']

    class Meta:
        model = Modality


class DirtyModalityModelAdmin(admin.ModelAdmin):
    list_display = ['dirty_name', 'modality']
    list_display_links = ['dirty_name', 'modality']
    list_filter = ['modality']
    serach_fields = ['dirty_name', 'modality']

    class Meta:
        model = DirtyModality


class ModalityClinicMapModelAdmin(admin.ModelAdmin):
    list_display = ['modality', 'clinic']
    list_display_links = ['modality', 'clinic']
    list_filter = ['clinic', 'modality']

    class Meta:
        model = ModalityClinicMap


class OperatorClinicMapModelAdmin(admin.ModelAdmin):
    list_display = ['operator', 'clinic']
    list_display_links = ['operator', 'clinic']
    list_filter = ['clinic']
    search_fields = ['clinic', 'operator']

    class Meta:
        model = OperatorClinicMap


class ExamModelAdmin(admin.ModelAdmin):
    list_display = ['exam_no', 'exam_description', 'exam_date', 'dirty_clinic', 'dirty_operator', 'dirty_modality',
                    'fluoro_time', 'dose']
    list_display_links = ['exam_no', 'exam_description', 'exam_date', 'dirty_clinic', 'dirty_operator',
                          'dirty_modality', 'fluoro_time', 'dose']

    class Meta:
        model = Exam


class ExamDescriptionModelAdmin(admin.ModelAdmin):
    list_display = ['description', 'anatomy_region', 'pediatric']
    list_display_links = ['description', 'anatomy_region', 'pediatric']
    list_filter = ['pediatric', 'anatomy_region']

    class Meta:
        model = ExamDescription


class AnatomyRegionModelAdmin(admin.ModelAdmin):
    list_display = ['region']
    list_display_links = ['region']

    class Meta:
        model = AnatomyRegion


class UpdatesModelAdmin(admin.ModelAdmin):
    list_display = ['updated', 'server', 'successful']
    list_display_links = ['updated', 'server', 'successful']
    list_filter = ['server', 'successful']

    class Meta:
        model = Updates


admin.site.register(Hospital, HospitalModelAdmin)
admin.site.register(DirtyClinic, DirtyClinicModelAdmin)
admin.site.register(Clinic, ClinicModelAdmin)
admin.site.register(ClinicCategory, ClinicCategoryModelAdmin)
admin.site.register(Operator, OperatorModelAdmin)
admin.site.register(DirtyOperator, DirtyOperatorModelAdmin)
admin.site.register(Modality, ModalityModelAdmin)
admin.site.register(DirtyModality, DirtyModalityModelAdmin)
admin.site.register(OperatorClinicMap, OperatorClinicMapModelAdmin)
admin.site.register(ModalityClinicMap, ModalityClinicMapModelAdmin)
admin.site.register(Exam, ExamModelAdmin)
admin.site.register(ExamDescription, ExamDescriptionModelAdmin)
admin.site.register(AnatomyRegion, AnatomyRegionModelAdmin)
admin.site.register(Updates, UpdatesModelAdmin)
