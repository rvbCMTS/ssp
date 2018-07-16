from rest_framework import serializers
from .models import Modality, RoiValue


class ModalityMeasurementSerializer(serializers.Serializer):

    class Meta:
        model = Modality
        fields = '__all__'

class ModalityReferenceSerializer(serializers.Serializer):

    class Meta:
        model = RoiValue
        fields = '__all__'