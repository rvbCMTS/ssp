from django.contrib import admin
from .models import ReportedMachine, Machine


class MachineModelAdmin(admin.ModelAdmin):
    list_display = ['display_name']
    list_display_links = ['display_name']
    search_fields = ['display_name']

    class Meta:
        model = Machine


class ReportedMachineModelAdmin(admin.ModelAdmin):
    list_display = ['device_serial_number', 'machine_model', 'machine']
    list_display_links = ['device_serial_number', 'machine_model', 'machine']
    list_filter = ['machine_model']
    search_fields = ['device_serial_number', 'machine_model', 'machine']

    class Meta:
        model = ReportedMachine


admin.site.register(Machine, MachineModelAdmin)
admin.site.register(ReportedMachine, ReportedMachineModelAdmin)
