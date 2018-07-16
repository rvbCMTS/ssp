from django.db import models


class Machine(models.Model):
    hospital_name = models.TextField(blank=False, null=False)
    host_identifier = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.hospital_name


class Protocols(models.Model):
    ris_name = models.TextField(blank=False, null=False)
    body_part = models.TextField(blank=False, null=False)
    technique = models.TextField(blank=False, null=False)
    kv = models.DecimalField(null=False, decimal_places=1, max_digits=4)
    mas = models.DecimalField(null=True, decimal_places=2, max_digits=5)
    filter_cu = models.DecimalField(null=False, decimal_places=1, max_digits=2)
    focus = models.IntegerField(null=False)
    diamond_view = models.TextField(blank=False, null=False)
    edge_filter_kernel_size = models.IntegerField(null=False)
    edge_filter_gain = models.DecimalField(null=False, decimal_places=2, max_digits=4)
    harmonization_kernel_size = models.IntegerField(null=False)
    harmonization_gain = models.DecimalField(null=False, decimal_places=2, max_digits=4)
    noise_reduction = models.BooleanField(blank=False, null=False)
    image_auto_amplification = models.BooleanField(blank=False, null=False)
    image_amplification_gain = models.DecimalField(null=True, decimal_places=1, max_digits=3)
    sensitivity = models.IntegerField(null=False)
    lut = models.TextField(blank=False, null=False)
    last_modification = models.TextField(blank=False, null=False)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)

    def __str__(self):
        return self.ris_name
