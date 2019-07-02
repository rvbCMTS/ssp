from rest_framework import serializers
from .models import Machine, ReportedMachine, AcrResult, ManufacturerModelName, AcrLog


class ManufacturerModelNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = ManufacturerModelName
        fields = ('id', 'name', 'manufacturer')


class MachineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Machine
        fields = ('id', 'display_name')


class ReportedMachineSerializer(serializers.ModelSerializer):
    machine = MachineSerializer(many=False, read_only=True, required=False)
    machine_model = ManufacturerModelNameSerializer(many=False)

    class Meta:
        model = ReportedMachine
        fields = ('id', 'device_serial_number', 'machine_model', 'machine')


class AcrResultSerializer(serializers.ModelSerializer):
    reported_machine = ReportedMachineSerializer(many=False, read_only=True)

    class Meta:
        model = AcrResult
        fields = (
            'id', 'patient_id', 'patient_weight', 'patient_position', 'folder', 'acquisition_time', 'study_time',
            'protocol_name', 'series_description', 'series_instance_uid', 'study_id', 'operator', 'operator_name',
            'reported_machine', 'software_version', 'receive_coil_name', 'echo_time', 'repetition_time',
            'actual_receive_gain_analog', 'actual_receive_gain_digital', 'auto_prescan_gain_digital',
            'auto_prescan_center_frequency', 'auto_prescan_transmit_gain', 'auto_prescan_analog_receiver_gain',
            'auto_prescan_digital_receiver_gain',
            'transmitting_coil_type', 'surface_coil_type', 'prescan_type', 'transmit_gain',
            'db_dt_peak_rate_of_change_of_gradient_field', 'ge_coil_name', 'image_frequency', 'pixel_bandwidth',
            'image_position', 'rotation', 'center_x', 'center_y', 'ghosting_ratio_slice5', 'ghosting_ratio_slice5_std',
            'max_roi_mean', 'min_roi_mean', 'percent_uniformity_integral', 'ghosting_ratio', 'noise',
            'slice_position_accuracy_slice1', 'slice_position_accuracy_slice11', 'slice_thickness',
            'diameter_x_slice1', 'diameter_y_slice1', 'diameter_diag1_slice1', 'diameter_diag2_slice1',
            'diameter_x_slice5', 'diameter_y_slice5', 'diameter_diag1_slice5', 'diameter_diag2_slice5',
            'ul_1_score', 'lr_1_score', 'ul_2_score', 'lr_2_score', 'ul_3_score', 'lr_3_score')


class AcrResultInsertSerializer(serializers.ModelSerializer):
    reported_machine = serializers.IntegerField()

    class Meta:
        model = AcrResult
        fields = (
            'id', 'patient_id', 'patient_weight', 'patient_position', 'folder', 'acquisition_time', 'study_time',
            'protocol_name', 'series_description', 'series_instance_uid', 'study_id', 'operator', 'operator_name',
            'reported_machine', 'software_version', 'receive_coil_name', 'echo_time', 'repetition_time',
            'actual_receive_gain_analog', 'actual_receive_gain_digital', 'auto_prescan_gain_digital',
            'auto_prescan_center_frequency', 'auto_prescan_transmit_gain', 'auto_prescan_analog_receiver_gain',
            'auto_prescan_digital_receiver_gain',
            'transmitting_coil_type', 'surface_coil_type', 'prescan_type', 'transmit_gain',
            'db_dt_peak_rate_of_change_of_gradient_field', 'ge_coil_name', 'image_frequency', 'pixel_bandwidth',
            'image_position', 'rotation', 'center_x', 'center_y', 'ghosting_ratio_slice5', 'ghosting_ratio_slice5_std',
            'max_roi_mean', 'min_roi_mean', 'percent_uniformity_integral', 'ghosting_ratio', 'noise',
            'slice_position_accuracy_slice1', 'slice_position_accuracy_slice11', 'slice_thickness',
            'diameter_x_slice1', 'diameter_y_slice1', 'diameter_diag1_slice1', 'diameter_diag2_slice1',
            'diameter_x_slice5', 'diameter_y_slice5', 'diameter_diag1_slice5', 'diameter_diag2_slice5',
            'ul_1_score', 'lr_1_score', 'ul_2_score', 'lr_2_score', 'ul_3_score', 'lr_3_score'
        )


class AcrLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = AcrLog
        fields = ('id', 'log_date', 'folder', 'read_level', 'read_message', 'series_instance_uid', 'echo_time',
                  'repetition_time', 'series_description', 'analysis_level', 'analysis_message')
