from django.db import models


class AcrLog(models.Model):
    log_date = models.DateTimeField(blank=False, null=False)
    folder = models.TextField(blank=True, null=True)
    read_level = models.CharField(max_length=45)
    read_message = models.TextField(blank=True, null=True)
    series_instance_uid = models.CharField(max_length=4000)
    echo_time = models.FloatField(blank=True, null=True)
    repetition_time = models.FloatField(blank=True, null=True)
    series_description = models.CharField(max_length=4000)
    analysis_level = models.CharField(max_length=45)
    analysis_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.log_date} - Read msg: {self.read_message}; Analysis msg: {self.analysis_message}'

    class Meta:
        ordering = ['-log_date']


class ManufacturerModelName(models.Model):
    name = models.CharField(max_length=400, blank=False, null=False)
    manufacturer = models.CharField(max_length=400, blank=False, null=False)

    def __str__(self):
        return f'{self.manufacturer} - {self.name}'

    class Meta:
        ordering = ['manufacturer', 'name']


class Machine(models.Model):
    display_name = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['display_name']


class ReportedMachine(models.Model):
    device_serial_number = models.TextField(blank=False, null=False)
    machine_model = models.ForeignKey(ManufacturerModelName, on_delete=models.PROTECT, related_name='machine_model')
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, blank=True, null=True, related_name='machine')

    def __str__(self):
        if self.machine:
            return f'{self.machine.display_name} ({self.machine_model.manufacturer.name}, {self.machine_model.name})'

    class Meta:
        ordering = ['machine', 'machine_model', 'device_serial_number']


class AcrResult(models.Model):
    patient_id = models.CharField(max_length=400, blank=False, null=False)
    patient_weight = models.FloatField(blank=True, null=True)
    patient_position = models.CharField(max_length=60, blank=True, null=True)
    folder = models.TextField(blank=True, null=True)
    acquisition_time = models.DateTimeField(blank=False, null=False)
    study_time = models.TimeField(blank=True, null=True)
    protocol_name = models.CharField(max_length=400, null=True)
    series_description = models.CharField(max_length=400, null=True)
    series_instance_uid = models.CharField(max_length=400, null=True)
    study_instance_uid = models.CharField(max_length=400, null=True)
    study_id = models.CharField(max_length=400, null=True)
    operator = models.CharField(max_length=400, null=True)
    operator_name = models.CharField(max_length=400, null=True)

    reported_machine = models.ForeignKey(ReportedMachine, on_delete=models.PROTECT, related_name='reported_machine')
    software_version = models.CharField(max_length=400)

    receive_coil_name = models.CharField(max_length=400, null=True)
    echo_time = models.FloatField(blank=True, null=True)
    repetition_time = models.FloatField(blank=True, null=True)
    actual_receive_gain_analog = models.FloatField(blank=True, null=True)
    actual_receive_gain_digital = models.FloatField(blank=True, null=True)
    auto_prescan_gain_digital = models.FloatField(blank=True, null=True)
    auto_prescan_center_frequency = models.FloatField(blank=True, null=True)
    auto_prescan_transmit_gain = models.FloatField(blank=True, null=True)
    auto_prescan_analog_receiver_gain = models.FloatField(blank=True, null=True)
    auto_prescan_digital_receiver_gain = models.FloatField(blank=True, null=True)

    transmitting_coil_type = models.IntegerField(blank=True, null=True)
    surface_coil_type = models.IntegerField(blank=True, null=True)
    prescan_type = models.IntegerField(blank=True, null=True)
    transmit_gain = models.FloatField(blank=True, null=True)
    db_dt_peak_rate_of_change_of_gradient_field = models.FloatField(blank=True, null=True)

    ge_coil_name = models.CharField(max_length=400, null=True)

    image_frequency = models.FloatField(blank=True, null=True)
    pixel_bandwidth = models.FloatField(blank=True, null=True)
    image_position = models.CharField(max_length=400, null=True)
    rotation = models.FloatField(blank=True, null=True)
    center_x = models.FloatField(blank=True, null=True)
    center_y = models.FloatField(blank=True, null=True)
    ghosting_ratio_slice5 = models.FloatField(blank=True, null=True)
    ghosting_ratio_slice5_std = models.FloatField(blank=True, null=True)
    max_roi_mean = models.FloatField(blank=True, null=True)
    min_roi_mean = models.FloatField(blank=True, null=True)
    percent_uniformity_integral = models.FloatField(blank=True, null=True)
    ghosting_ratio = models.FloatField(blank=True, null=True)
    noise = models.FloatField(blank=True, null=True)
    slice_position_accuracy_slice1 = models.FloatField(blank=True, null=True)
    slice_position_accuracy_slice11 = models.FloatField(blank=True, null=True)
    slice_thickness = models.FloatField(blank=True, null=True)
    diameter_x_slice1 = models.FloatField(blank=True, null=True)
    diameter_y_slice1 = models.FloatField(blank=True, null=True)
    diameter_diag1_slice1 = models.FloatField(blank=True, null=True)
    diameter_diag2_slice1 = models.FloatField(blank=True, null=True)
    diameter_x_slice5 = models.FloatField(blank=True, null=True)
    diameter_y_slice5 = models.FloatField(blank=True, null=True)
    diameter_diag1_slice5 = models.FloatField(blank=True, null=True)
    diameter_diag2_slice5 = models.FloatField(blank=True, null=True)
    ul_1_score = models.FloatField(blank=True, null=True)
    lr_1_score = models.FloatField(blank=True, null=True)
    ul_2_score = models.FloatField(blank=True, null=True)
    lr_2_score = models.FloatField(blank=True, null=True)
    ul_3_score = models.FloatField(blank=True, null=True)
    lr_3_score = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'{self.acquisition_time} ({self.reported_machine})'

    class Meta:
        ordering = ['-acquisition_time']
