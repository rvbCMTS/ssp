from django.db import models
from ckeditor.fields import RichTextField


class Contact(models.Model):
    last_name = models.CharField(max_length=400, blank=False, null=False)
    first_name = models.CharField(max_length=400, blank=False, null=False)
    role = models.CharField(max_length=4000, blank=True, null=True)
    phone_number = models.CharField(max_length=400, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'


class City(models.Model):
    city = models.CharField(max_length=400, blank=False, null=False)

    def __str__(self):
        return self.city


class Clinic(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.DO_NOTHING, blank=True, null=True)
    clinic = models.CharField(max_length=4000, blank=False, null=False)

    def __str__(self):
        return f'{self.clinic} ({self.city})'


class RadiationProtectionClass(models.Model):
    protection_class = models.CharField(max_length=4000, blank=False, null=False)
    class_description = RichTextField(blank=True, null=True)

    def __str__(self):
        return self.protection_class


class Room(models.Model):
    room_number = models.CharField(max_length=4000, blank=False, null=False)
    room_name = models.CharField(max_length=4000, blank=True, null=True)
    clinic = models.ForeignKey(Clinic, blank=False, null=False, on_delete=models.CASCADE)
    room_width = models.FloatField(blank=True, null=True)
    room_length = models.FloatField(blank=True, null=True)
    protection_class = models.ForeignKey(RadiationProtectionClass, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.room_number} - {self.clinic}'
