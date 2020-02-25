from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Profession(models.Model):
    landauer_profession_id = models.IntegerField(blank=True, null=True, unique=True)
    profession = models.CharField(max_length=4000, blank=False, null=False)

    def __str__(self):
        return self.profession

    class Meta:
        ordering = ['profession']


class Personnel(models.Model):
    dosimetry_vendor_id = models.CharField(max_length=4000, blank=True, null=True)
    person_id = models.CharField(max_length=400, blank=True, null=True)
    person_name = models.CharField(max_length=400, blank=False, null=False)
    profession = models.ForeignKey(Profession, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return f'{self.person_name} ({self.profession})'

    class Meta:
        permissions = (
            ("view_personnel_names", "Can see name of personnel"),
            ("view_personnel_pid", "Can see pid of the personnel"),
        )
        unique_together = (('person_id', 'dosimetry_vendor_id'),)
        ordering = ['person_name']


class DosimeterPlacement(models.Model):
    dosimeter_placement = models.CharField(max_length=400, blank=False, null=False, unique=True)

    def __str__(self):
        return self.dosimeter_placement


class DosimeterLaterality(models.Model):
    dosimeter_laterality = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.dosimeter_laterality


class VendorDosimeterPlacement(models.Model):
    vendor_dosimeter_placement = models.CharField(max_length=4000, blank=False, null=False, unique=True)
    dosimeter_placement = models.ForeignKey(DosimeterPlacement, on_delete=models.DO_NOTHING, blank=True, null=True)
    dosimeter_laterality = models.ForeignKey(DosimeterLaterality, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.vendor_dosimeter_placement


class ClinicDisplayName(models.Model):
    display_name = models.CharField(max_length=400, blank=False, null=False)

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ('display_name',)


class Clinic(models.Model):
    clinic = models.CharField(max_length=4000, blank=False, null=False, unique=True)
    display_clinic = models.CharField(max_length=400, blank=False, null=False, default=clinic)
    display_name = models.ForeignKey(ClinicDisplayName, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.display_clinic

    class Meta:
        ordering = ('display_name__display_name',)


class Result(models.Model):
    dosimetry_vendor = models.CharField(max_length=4000, blank=True, null=True)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    dosimeter_type = models.CharField(max_length=400, null=True, blank=True)
    vendor_dosimetry_placement = models.ForeignKey(VendorDosimeterPlacement, on_delete=models.DO_NOTHING)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    report = models.CharField(max_length=4000, blank=True, null=True)
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


class NotReturnedDosimeters(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    report = models.CharField(max_length=4000, blank=False, null=False)

    def __str__(self):
        return f'{self.personnel.person_name} ({self.report})'

    class Meta:
        ordering = ['personnel', 'report']


FULL_BODY_ASSESSMENT = (
    ('ok', 'Ok'),
    ('an', 'Ok med anmärkning'),
    ('no', 'Inte Ok'),
)


class FullBodyDosimetry(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, blank=False, null=False)
    measurement_date = models.DateTimeField(blank=False, null=False)
    result = models.CharField(max_length=2, choices=FULL_BODY_ASSESSMENT, null=False)
    comment = models.CharField(max_length=4000, null=True, blank=True)

    def __str__(self):
        return f'{self.measurement_date.strftime("%Y-%m-%d")} - {self.personnel.person_name}'

    class Meta:
        ordering = ['measurement_date', 'personnel']
        permissions = (
            ("manage_full_body_results", "Can see and perform full body measurements"),
        )
        unique_together = (('personnel', 'measurement_date'),)
