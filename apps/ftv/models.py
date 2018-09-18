from django.db import models
from apps.radiation_shielding.models import Room, RadiationProtectionClass
from ckeditor.fields import RichTextField


class Manufacturer(models.Model):
    manufacturer = models.CharField(max_length=4000, blank=False, null=False)

    def __str__(self):
        return self.manufacturer


class ManufacturerModel(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, blank=False, null=False, on_delete=models.CASCADE)
    model = models.CharField(max_length=4000, blank=False, null=False)
    qa_instruction = RichTextField(blank=True, null=True)

    def __str__(self):
        return f'{self.model} ({self.manufacturer})'


class MachineType(models.Model):
    machine_type = models.CharField(max_length=4000, blank=False, null=False)
    required_protection_class = models.ForeignKey(RadiationProtectionClass, blank=True, null=True,
                                                  on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.machine_type


class InstructionType(models.Model):
    instruction_type = models.CharField(max_length=400, blank=False, null=False)

    def __str__(self):
        return self.instruction_type


class QaTestInstructions(models.Model):
    instruction_name = models.CharField(max_length=400, blank=False, null=False)
    instruction = RichTextField(blank=False, null=False)
    instruction_type = models.ForeignKey(InstructionType, blank=False, null=False, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.instruction_name} ({self.instruction_type})'

    class Meta:
        ordering = ['instruction_type', 'instruction_name']


class Machine(models.Model):
    machine_name = models.CharField(max_length=400, blank=False, null=False)
    inventory_system_id = models.CharField(max_length=400, blank=True, null=True)
    model = models.ForeignKey(ManufacturerModel, blank=False, null=False, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, blank=False, null=False, on_delete=models.CASCADE)
    machine_type = models.ForeignKey(MachineType, blank=False, null=False, on_delete=models.DO_NOTHING)
    in_use = models.BooleanField(blank=False, null=False, default=True)
    installed_date = models.DateField(blank=False, null=False)
    taken_out_of_commission_date = models.DateField(blank=True, null=True)
    qa_test_instruction = models.ManyToManyField(QaTestInstructions)

    def __str__(self):
        return self.machine_name

    class Meta:
        ordering = ['-in_use', 'machine_name']


class OP300TestQA(models.Model):
    machine = models.ForeignKey(Machine, blank=False, null=False, on_delete=models.DO_NOTHING)
    qa_date = models.DateTimeField(blank=False, null=False)
    signature = models.CharField(max_length=400, blank=False, null=False)
    comment = models.CharField(max_length=4000, blank=True, null=True)

    def __str__(self):
        return f'{self.machine} - {self.qa_date}'

    class Meta:
        ordering = ['-qa_date', 'machine']


class OP300PanTest(models.Model):
    test = models.ForeignKey(OP300TestQA, blank=False, null=False, on_delete=models.CASCADE)
    calibration_run = models.BooleanField(blank=False, null=False, default=False)
    pan_geom = models.BooleanField(blank=False, null=False, default=False)
    pan_geom_x_offset = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    pan_geom_y_offset = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    pan_geom_n_offset = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    pan_geom_j_offset = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    pan_pix = models.BooleanField(blank=False, null=False, default=False)
    pan_pix_ctq = models.DecimalField(max_digits=8, decimal_places=2)
    pan_pix_signal_level = models.IntegerField(blank=False, null=False)
    pan_pix_dark_level = models.IntegerField(blank=False, null=False)
    pan_qc = models.NullBooleanField(blank=True, null=True)
    pan_qc_homogeneous = models.NullBooleanField(blank=True, null=True)
    pan_qc_high_contrast = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    pan_qc_low_contrast = models.NullBooleanField(blank=True, null=True)
    pan_qc_round_ball = models.NullBooleanField(blank=True, null=True)
    pan_qc_distance_white_rods_ball = models.NullBooleanField(blank=True, null=True)


class OP300CefTest(models.Model):
    test = models.ForeignKey(OP300TestQA, blank=False, null=False, on_delete=models.CASCADE)
    calibration_run = models.BooleanField(blank=False, null=False, default=False)
    cef_pix = models.BooleanField(blank=False, null=False, default=False)
    cef_qc = models.NullBooleanField(blank=True, null=True)
    cef_qc_homogeneous = models.NullBooleanField(blank=True, null=True)
    cef_qc_high_contrast = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    cef_qc_low_contrast = models.NullBooleanField(blank=True, null=True)


class OP300CBCTTest(models.Model):
    test = models.ForeignKey(OP300TestQA, blank=False, null=False, on_delete=models.CASCADE)
    calibration_run = models.BooleanField(blank=False, null=False, default=False)
    cbct_geom = models.BooleanField(blank=False, null=False, default=False)
    cbct_geom_x_offset = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    cbct_geom_y_offset = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    cbct_geom_n_offset = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    cbct_geom_j_offset = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    cbct_geom_scan_diff = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    cbct_geom_ctq = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False)
    cbct_pix = models.BooleanField(blank=False, null=False, default=False)
    cbct_pix_ctq = models.DecimalField(max_digits=8, decimal_places=2)
    cbct_pix_signal_level = models.IntegerField(blank=False, null=False)
    cbct_pix_dark_level = models.IntegerField(blank=False, null=False)
    cbct_qc = models.NullBooleanField(blank=True, null=True)
    cbct_qc_pmma_min_value = models.IntegerField(blank=True, null=True)
    cbct_qc_pmma_max_value = models.IntegerField(blank=True, null=True)
    cbct_qc_pmma_max_std_dev = models.IntegerField(blank=True, null=True)
    cbct_qc_ptfe_value = models.IntegerField(blank=True, null=True)
    cbct_qc_ptfe_std_dev = models.IntegerField(blank=True, null=True)
    cbct_qc_air_value = models.IntegerField(blank=True, null=True)
    cbct_qc_air_std_dev = models.IntegerField(blank=True, null=True)


class IntraOralYearlyQA(models.Model):
    machine = models.ForeignKey(Machine, blank=False, null=False, on_delete=models.DO_NOTHING)
    qa_date = models.DateTimeField(blank=False, null=False)
    # signature = models.ForeignKey(User, blank=False, null=False, on_delet=models.DO_NOTHING)
