from rest_framework import serializers
from .models import WorkOrder


class WorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = '__all__'
        depth = 1
