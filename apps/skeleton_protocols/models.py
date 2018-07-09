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
    kv = models.IntegerField(null=False)
    mas = models.IntegerField(null=False)
    filter_cu = models.IntegerField(null=False)
    focus = models.IntegerField(null=False)
    diamond_view = models.TextField(blank=False, null=False)
    edge_filter_kernel_size = models.IntegerField(null=False)
    edge_filter_gain = models.IntegerField(null=False)
    harmonization_kernel_size = models.IntegerField(null=False)
    harmonization_gain = models.IntegerField(null=False)
    noise_reduction = models.TextField(blank=False, null=False)
    image_auto_amplification = models.TextField(blank=False, null=False)
    image_amplification_gain = models.IntegerField(null=True)
    sensitivity = models.IntegerField(null=False)
    lut = models.TextField(blank=False, null=False)
    last_modification = models.TextField(blank=False, null=False)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)

    technique_choices = (
        ('1 pt', '1 pt'),
        ('2 pt', '2 pt'),
    )

    sensitivity_choices = (
        (400, '400'),
        (800, '800'),
    )

    def __str__(self):
        return self.ris_name
