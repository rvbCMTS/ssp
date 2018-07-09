from django.db import models


class Modality(models.Model):
    location = models.TextField(blank=False, null=False)
    room = models.TextField(blank=False, null=False)
    display_name = models.TextField(blank=False, null=False)
    maximo_number = models.TextField(blank=True, null=True)
    manufacturer = models.TextField(blank=False, null=False)
    manufacturer_model = models.TextField(blank=False, null=False)
    in_use = models.BooleanField(null=False, default=True)
    number_of_rois = models.IntegerField(blank=False, null=False)
    instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['display_name']


class References(models.Model):
    modality = models.ForeignKey(Modality, on_delete=models.CASCADE)
    parameter = models.CharField(max_length=200, blank=False, null=False)
    parameter_value = models.FloatField(blank=False, null=False)
    tolerance = models.FloatField(blank=False, null=False)
    tolerance_unit = models.CharField(max_length=60)
    set_date = models.DateField(blank=False, null=False)
    active = models.BooleanField(blank=False, null=False, default=True)
    
    def __str__(self):
        return f'{self.parameter}: {self.parameter_value}'

    class Meta:
        ordering = ['active', 'parameter', '-set_date']


class Measurement(models.Model):
    modality = models.ForeignKey(Modality, on_delete=models.CASCADE)
    measurement_date = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    mas = models.FloatField(blank=False, null=False)
    entrance_dose = models.FloatField(blank=False, null=False)
    comment = models.TextField(blank=True, null=True)
    signature = models.CharField(max_length=200, null=False)

    def __str__(self):
        return f'{self.modality.display_name} - {self.measurement_date}'

    class Meta:
        ordering = ['-measurement_date']


class RoiValues(models.Model):
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    roi = models.IntegerField(blank=False, null=False)
    mean = models.FloatField(blank=False, null=False)
    stdev = models.FloatField(blank=False, null=False)
    signal_noise_ratio = models.FloatField(blank=False, null=False)

    def __str__(self):
        return f'{self.roi} ({self.measurement})'

    class Meta:
        ordering = ['measurement', 'roi']
