from django import forms
from django.contrib import admin
from .models import Manufacturer, ManufacturerModel, MachineType, Machine
from ckeditor.widgets import CKEditorWidget


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['manufacturer']
    list_display_links = ['manufacturer']
    search_fields = ['manufacturer']

    class Meta:
        model = Manufacturer


class ManufacturerModelAdminForm(forms.ModelForm):
    instructions = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = ManufacturerModel
        fields = '__all__'


class ManufacturerModelAdmin(admin.ModelAdmin):
    list_display = ['manufacturer', 'model', 'qa_instruction']
    list_display_links = ['manufacturer', 'model', 'qa_instruction']
    list_filter = ['manufacturer']
    search_fields = ['manufacturer', 'model', 'qa_instruction']
    form = ManufacturerModelAdminForm

    class Meta:
        model = ManufacturerModel


class MachineTypeAdmin(admin.ModelAdmin):
    list_display = ['machine_type', 'required_protection_class']
    list_display_links = ['machine_type', 'required_protection_class']
    list_filter = ['machine_type']
    search_fields = ['machine_type', 'required_protection_class']
    form = ManufacturerModelAdminForm

    class Meta:
        model = MachineType


class MachineAdmin(admin.ModelAdmin):
    list_display =          ['machine_name', 'inventory_system_id','model', 'room', 'machine_type', 'in_use',
                             'installed_date', 'taken_out_of_commission_date']
    list_display_links =    ['machine_name', 'inventory_system_id','model', 'room', 'machine_type', 'in_use',
                             'installed_date', 'taken_out_of_commission_date']
    list_filter =           ['machine_type', 'model']
    search_fields =         ['machine_name', 'inventory_system_id','model', 'room', 'machine_type', 'in_use',
                             'installed_date', 'taken_out_of_commission_date']
    form = ManufacturerModelAdminForm

    class Meta:
        model = Machine


admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(ManufacturerModel, ManufacturerModelAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineType, MachineTypeAdmin)

