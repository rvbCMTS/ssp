from django import forms
from django.contrib import admin
from .models import Contact, City, Clinic, Room, RadiationProtectionClass
from ckeditor.widgets import CKEditorWidget


class RadiationProtectionClassAdminForm(forms.ModelForm):
    class_description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = RadiationProtectionClass
        fields = '__all__'


class ContactAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'role', 'phone_number', 'email']
    list_display_links = ['last_name', 'first_name', 'role', 'phone_number', 'email']
    list_filter = ['role']
    search_fields = ['last_name', 'first_name', 'role', 'phone_number', 'email']

    class Meta:
        model = Contact


class CityAdmin(admin.ModelAdmin):
    list_display = ['city']
    list_display_links = ['city']
    search_fields = ['city']

    class Meta:
        model = City


class ClinicAdmin(admin.ModelAdmin):
    list_display = ['city', 'contact', 'clinic']
    list_display_links = ['city', 'contact', 'clinic']
    list_filter = ['city']
    search_fields = ['city', 'clinic']

    class Meta:
        model = Clinic


class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_name', 'clinic', 'room_width', 'room_length']
    list_display_links = ['room_number', 'room_name', 'clinic', 'room_width', 'room_length']
    list_filter = ['clinic']
    search_fields = ['room_number', 'room_name', 'clinic', 'room_width', 'room_length']

    class Meta:
        model = Room


class RadiationProtectionClassAdmin(admin.ModelAdmin):
    list_display = ['protection_class', 'class_description']
    list_display_links = ['protection_class']
    search_fields = ['protection_class', 'class_description']
    form = RadiationProtectionClassAdminForm

    class Meta:
        model = RadiationProtectionClass


admin.site.register(Contact, ContactAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Clinic, ClinicAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(RadiationProtectionClass, RadiationProtectionClassAdmin)
