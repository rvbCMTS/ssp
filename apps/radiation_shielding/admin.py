from django.contrib import admin
from .models import (City, ShieldingClassification, Department, Room)


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
    list_display = ['department']
    list_display_links = ['department']
    list_filter = []

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


admin.site.register(City, CityModelAdmin)
admin.site.register(ShieldingClassification, ShieldingClassificationModelAdmin)
admin.site.register(Department, DepartmentModelAdmin)
admin.site.register(Room, RoomModelAdmin)
