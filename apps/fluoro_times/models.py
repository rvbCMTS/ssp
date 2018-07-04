from django.db import models


class Hospital(models.Model):
    name = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ClinicCategory(models.Model):
    name = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Clinic(models.Model):
    name = models.TextField(blank=False, null=False)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True)
    clinic_category = models.ForeignKey(ClinicCategory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.name} - {self.hospital.name}'

    class Meta:
        ordering = ['name', 'hospital']


class DirtyClinic(models.Model):
    dirty_name = models.TextField(blank=False, null=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.name} ({self.clinic})'

    class Meta:
        ordering = ['clinic', 'dirty_name']


class Operator(models.Model):
    first_name = models.TextField(blank=False, null=False)
    last_name = models.TextField(blank=False, null=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.last_name}, {self.last_name} ({self.clinic.name})'

    class Meta:
        ordering = ['last_name', 'first_name']


class DirtyOperator(models.Model):
    dirty_name = models.TextField(blank=False, null=False)
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.dirty_name

    class Meta:
        ordering = ['operator', 'dirty_name']


DOSE_UNITS = (
    ('gm', 'Gym2'),
    ('gdm', 'Gydm2'),
    ('gcm', 'Gycm2'),
    ('dgm', 'dGym2'),
    ('dgdm', 'dGydm2'),
    ('dgcm', 'dGycm2'),
    ('cgm', 'cGym2'),
    ('cgdm', 'cGydm2'),
    ('cgcm', 'cGycm2')
)

DOSE_CONV_FACTOR = {
    'gm': 10000,
    'gdm': 100,
    'gcm': 1,
    'dgm': 1000,
    'dgdm': 10,
    'dgcm': 0.1,
    'cgm': 100,
    'cgdm': 1,
    'cgcm': 100
}


class Modality(models.Model):
    name = models.TextField(blank=False, null=False)
    dose_unit = models.CharField(max_length=4, choices=DOSE_UNITS, null=True)
    active = models.BooleanField(null=False, default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class DirtyModality(models.Model):
    dirty_name = models.TextField(blank=False, null=False)
    modality = models.ForeignKey(Modality, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.dirty_name

    class Meta:
        ordering = ['dirty_name']


class AnatomyRegion(models.Model):
    region = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.region

    class Meta:
        ordering = ['region']


class ExamDescription(models.Model):
    description = models.TextField(blank=False, null=False)
    anatomy_region = models.ForeignKey(AnatomyRegion, on_delete=models.SET_NULL, null=True)
    pediatric = models.BooleanField(null=False, default=False)

    def __str__(self):
        return f'{self.description} (Pediatric: {self.pediatric})'

    class Meta:
        ordering = ['description']


class Exam(models.Model):
    exam_no = models.TextField(blank=False, null=False)
    exam_description = models.ForeignKey(ExamDescription, on_delete=models.CASCADE)
    exam_date = models.DateTimeField(blank=False, null=False)
    dirty_clinic = models.ForeignKey(DirtyClinic, on_delete=models.PROTECT)
    dirty_operator = models.ForeignKey(DirtyOperator, on_delete=models.PROTECT)
    dirty_modality = models.ForeignKey(DirtyModality, on_delete=models.PROTECT)
    fluoro_time = models.FloatField(blank=False, null=False)
    dose = models.DecimalField(max_digits=16, decimal_places=4, null=True)

    def __str__(self):
        return f'{self.exam_date} - {self.exam_description}'

    class Meta:
        ordering = ['-exam_date']


class ModalityClinicMap(models.Model):
    modality = models.ForeignKey(Modality, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.clinic} - {self.modality.name}'

    class Meta:
        ordering = ['clinic', 'modality']


class OperatorClinicMap(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.clinic} - {self.operator.last_name}, {self.operator.first_name}'

    class Meta:
        ordering = ['clinic', 'operator']
