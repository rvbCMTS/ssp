from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Profession(models.Model):
    profession = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.profession


class Personnel(models.Model):
    dosimetry_vendor_id = models.TextField(blank=True, null=True)
    person_id = models.TextField(blank=True, null=True)
    person_name = models.TextField(blank=False, null=False)
    profession = models.ForeignKey(Profession, on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{} ({})'.format(self.person_name, self.profession)


class DosimeterPlacement(models.Model):
    dosimeter_placement = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.dosimeter_placement


class VendorDosimeterPlacement(models.Model):
    vendor_dosimeter_placement = models.TextField(blank=False, null=False)
    dosimeter_placement = models.ForeignKey(DosimeterPlacement, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.vendor_dosimeter_placement


class Clinic(models.Model):
    clinic = models.TextField(blank=False, null=False)
    display_clinic = models.TextField(blank=False, null=False, default=clinic)

    def __str__(self):
        return self.display_clinic

    class Meta:
        ordering = ('display_clinic',)


class Result(models.Model):
    dosimetry_vendor = models.TextField(blank=True, null=True)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    vendor_dosimetry_placement = models.ForeignKey(VendorDosimeterPlacement, on_delete=models.DO_NOTHING)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    report = models.TextField(blank=True, null=True)
    measurement_period_start = models.DateTimeField(blank=False, null=False)
    measurement_period_stop = models.DateTimeField(blank=False, null=False)
    measurement_period_center = models.DateField(blank=False, null=False)
    hp10 = models.FloatField(blank=True, null=True)
    hp007 = models.FloatField(blank=True, null=True)
    hp10fn = models.FloatField(blank=True, null=True)
    hp10tn = models.FloatField(blank=True, null=True)
    other_measure = models.TextField(blank=True, null=True)
    production = models.FloatField(blank=True, null=True)
    production_isotope = models.TextField(blank=True, null=True)
    yearly_production = models.FloatField(blank=True, null=True)
    deviation = models.BooleanField(blank=False, default=False)
    spot_check = models.BooleanField(blank=False, default=False)
    area_measurement = models.BooleanField(blank=False, default=False)

    def __str__(self):
        return '{} {} - {}'.format(self.personnel, self.measurement_period_start, self.measurement_period_stop)


class Deviation(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='deviant_result')
    comment = models.TextField(blank=False, null=False)
    reported_to_authority = models.BooleanField(blank=False, default=False)

    def __str__(self):
        return '{}: {}'.format(self.result, self.comment)


class PersonnelDosimetryUsers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='PersonnelDosimetry')
    local_administrator = models.BooleanField(default=False)
    clinics = models.ManyToManyField(Clinic)
    personnel_dosimetry_admin = models.BooleanField(default=False)
    inhouse_measurement_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user

    class Meta:
        ordering = ('user',)
