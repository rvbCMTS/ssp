from rest_framework import serializers
from .models import Exam, ExamDescription, AnatomyRegion, DirtyClinic, Clinic, ClinicCategory


class FluoroTimesField(serializers.RelatedField):
    def to_representation(self, value):
        return value.total_fluoro_time


class ExamSummarySerializer(serializers.Serializer):
    year = serializers.DateTimeField(read_only=True)
    exam_description__anatomy_region = serializers.CharField(allow_blank=True, required=False, read_only=True)
    total_fluoro_time = FluoroTimesField(many=True, read_only=True)


