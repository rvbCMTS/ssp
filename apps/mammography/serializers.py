from rest_framework import serializers

from .models import Modality, Reference, MeasurementParameter, Measurement, RoiValue



class ReferenceSerializer(serializers.Serializer):

    class Meta:
        model = Reference
        fields = ('roi', 'mean', 'stdev', 'signal_noise_ratio')


class MeasurementParameterSerializer(serializers.Serializer):
    reference = ReferenceSerializer(many=True, read_only=True)

    class Meta:
        model = MeasurementParameter
        fields = ('parameter')


class RoiValueSerializer(serializers.Serializer):

    class Meta:
        model = RoiValue


class MeasurementSerializer(serializers.Serializer):
    roi_values = RoiValueSerializer(many=True, read_only=True)

    class Meta:
        model = Measurement
        fields = ('modality', 'measurement_date', 'mas', 'entrance_dose', 'comment', 'signature')


class ModalityReferenceSerializer(serializers.Serializer):
    measurement_parameters = MeasurementParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Modality
        fields = '__all__'


class ModalityMeasurementSerializer(serializers.Serializer):
    measurements = MeasurementSerializer(many=True, read_only=True)

    class Meta:
        model = Modality
        fields = '__all__'
