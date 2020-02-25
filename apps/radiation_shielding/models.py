from django.core.validators import URLValidator
from django.db import models
from ckeditor.fields import RichTextField


class City(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class DepartmentCategory(models.Model):
    constant = models.CharField(max_length=200, blank=False, null=False)
    category = models.CharField(max_length=200, blank=False, null=False)

    def __str__(self):
        return self.constant

    def save(self, *args, **kwargs):
        self.constant = self.category.upper().strip().replace(' ', '_').replace('-', '')
        super(DepartmentCategory, self).save(*args, **kwargs)


class Department(models.Model):
    departmentName = models.CharField(max_length=200, blank=False, null=False)
    departmentCategory = models.ForeignKey(to=DepartmentCategory, on_delete=models.SET_NULL,
                                           blank=True, null=True)

    def __str__(self):
        return self.departmentName

    class Meta:
        ordering = ['departmentName']


class Clinic(models.Model):
    city = models.ForeignKey(to=City, on_delete=models.CASCADE, related_name='city')
    clinicName = models.CharField(max_length=400, blank=False, null=False)
    department = models.ForeignKey(to=Department, on_delete=models.SET_NULL, related_name='department',
                                   blank=True, null=True)

    def __str__(self):
        return self.clinicName

    class Meta:
        ordering = ['clinicName', 'city']


class ShieldingClassification(models.Model):
    constant = models.CharField(max_length=200, blank=True, null=False)
    classification = models.CharField(max_length=200, blank=False, null=False)
    requiredShielding = models.DecimalField(max_digits=10, decimal_places=3, blank=False, null=False)
    requiredShieldingUnit = models.CharField(max_length=10, blank=False, null=False)

    def __str__(self):
        return self.constant

    def save(self, *args, **kwargs):
        self.constant = self.classification.upper().strip().replace(' ', '_').replace('-', '')
        super(ShieldingClassification, self).save(*args, **kwargs)


class LocalFilePathField(models.URLField):
    default_validators = [URLValidator(schemes=['file'])]


class Room(models.Model):
    clinic = models.ForeignKey(to=Clinic, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='clinic')
    room = models.CharField(max_length=200, blank=False, null=False)
    roomWidth = models.FloatField(blank=True, null=True)
    roomLength = models.FloatField(blank=True, null=True)
    modalityType = models.CharField(max_length=100, blank=True, null=True)
    shielding = RichTextField(blank=True, null=True)
    shieldingClassification = models.ForeignKey(to=ShieldingClassification, on_delete=models.SET_NULL,
                                                blank=True, null=True, related_name='shield')
    shieldingClassificationDate = models.DateTimeField(blank=True, null=True)
    shieldingClassificationSignature = models.CharField(max_length=400, blank=True, null=True)
    shieldingClassificationComment = models.CharField(max_length=4000, blank=True, null=True)
    drawing = models.CharField(max_length=4000, blank=True, null=True)

    def __str__(self):
        return f'{self.room} ({self.clinic.clinicName})'

    class Meta:
        ordering = ['clinic__department', 'clinic__clinicName', 'room']

    def save(self, *args, **kwargs):
        if self.drawing:
            self.drawing = self.drawing.replace('\\', '/').replace(' ', '%20')
            if not self.drawing.lower().startswith('file:///'):
                self.drawing = f'file:///{self.drawing}'
        super(Room, self).save(*args, **kwargs)
