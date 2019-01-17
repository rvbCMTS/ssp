from rest_framework import serializers

from .models import Modality, Reference, MeasurementParameter, Measurement, RoiValue


class ReferenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reference
        depth = 1
        fields = '__all__'


class MeasurementParameterSerializer(serializers.ModelSerializer):
    reference = ReferenceSerializer(many=True, read_only=True)

    class Meta:
        model = MeasurementParameter
        fields = ('parameter')


class RoiValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoiValue
        depth = 1
        fields = '__all__'


class MeasurementSerializer(serializers.ModelSerializer):
    measurement_date = serializers.DateTimeField("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Measurement
        fields = '__all__'


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


class MeanAllRoiSerializer(serializers.Serializer):
    measurement_date = serializers.DateTimeField(read_only=True)
    mean_all = serializers.FloatField(read_only=True)


class ModalityResultSerializer(serializers.Serializer):
    roi_result = RoiValueSerializer(many=True)
    reference = ReferenceSerializer(many=True)
