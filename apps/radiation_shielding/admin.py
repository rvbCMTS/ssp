from django.contrib import admin
from .models import (City, ShieldingClassification, Department, Room, Clinic)


class CityModelAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    list_filter = []

    class Meta:
        model = City


class ShieldingClassificationModelAdmin(admin.ModelAdmin):
    list_display = ['constant', 'requiredShielding', 'requiredShieldingUnit']
    list_display_links = ['constant', 'requiredShielding', 'requiredShieldingUnit']
    list_filter = []

    class Meta:
        model = ShieldingClassification


class DepartmentModelAdmin(admin.ModelAdmin):
    list_display = ['departmentName', 'departmentCategory']
    list_display_links = ['departmentName', 'departmentCategory']
    list_filter = ['departmentCategory']

    class Meta:
        model = Department


class RoomModelAdmin(admin.ModelAdmin):
    list_display = ['clinic', 'room', 'roomWidth', 'roomLength', 'shielding', 'shieldingClassification',
                    'shieldingClassificationDate', 'shieldingClassificationSignature',
                    'shieldingClassificationSignature']
    list_display_links = ['clinic', 'room', 'roomWidth', 'roomLength', 'shielding', 'shieldingClassification',
                          'shieldingClassificationDate', 'shieldingClassificationSignature',
                          'shieldingClassificationSignature']
    list_filter = ['clinic']

    class Meta:
        model = Room


class ClinicModelAdmin(admin.ModelAdmin):
    list_display = ['city', 'clinicName', 'department']
    list_display_links = ['city', 'clinicName', 'department']
    list_filter = ['city', 'department']

    class Meta:
        model = Clinic


admin.site.register(City, CityModelAdmin)
admin.site.register(ShieldingClassification, ShieldingClassificationModelAdmin)
admin.site.register(Department, DepartmentModelAdmin)
admin.site.register(Room, RoomModelAdmin)
admin.site.register(Clinic, ClinicModelAdmin)
