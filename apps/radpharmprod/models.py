from django.db import models
from .helpers import get_formatted_half_life


class Radiopharmaceutical(models.Model):
    name = models.CharField(max_length=400, blank=False, null=False)
    half_life = models.FloatField(blank=True, null=True)

    def __str__(self):
        return get_formatted_half_life(self.half_life)


class Production(models.Model):
    radiopharmaceutical = models.ForeignKey(Radiopharmaceutical, on_delete=models.CASCADE, null=False)
    datum = models.DateTimeField(blank=False, null=False)
    activity_mbq = models.FloatField(blank=False, null=False)
    volume_ml = models.FloatField(blank=False, null=True)
    batch = models.CharField(max_length=400, blank=True, null=True, unique=True)
    signature = models.CharField(max_length=400, blank=False, null=False)

    def __str__(self):
        return f'{self.radiopharmaceutical.name} ({self.activity_mbq} MBq) {self.datum.strftime("%Y-%m-%d %H:%M:%S")}'

    class Meta:
        ordering = ['radiopharmaceutical', '-datum']


class Administration(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE, null=False)
    patient_weight = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=False)
    desired_administration_time = models.TimeField(null=False)
    desired_activity = models.DecimalField(max_digits=8, decimal_places=1)
    activity_in_syringe_time = models.TimeField(null=True, blank=False)
    activity_in_syringe = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=False)
    activity_left_in_syringe_time = models.TimeField(null=True, blank=False)
    activity_left_in_syringe = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=False)

    class Meta:
        ordering = ['production']


class ReadFiles(models.Model):
    radiopharmaceutical = models.ForeignKey(Radiopharmaceutical, on_delete=models.CASCADE, null=False)
    file = models.CharField(max_length=4000, null=False, blank=False)
    successful = models.BooleanField(blank=False, null=False)

    def __str__(self):
        return f'{self.radiopharmaceutical.name} - ({"Success" if self.successful else "Fail"}) {self.file}'

    class Meta:
        ordering = ['radiopharmaceutical', 'file']
