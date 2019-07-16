from rest_framework import serializers
from .models import (Clinic, City, ShieldingClassification, Department, DepartmentCategory, Room)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class DepartmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentCategory
        fields = ['id', 'constant', 'category']


class DepartmentSerializer(serializers.ModelSerializer):
    departmentCategory = DepartmentCategorySerializer(many=False, read_only=True)
    class Meta:
        model = Department
        fields = ['id', 'departmentName', 'departmentCategory']


class ClinicSerializer(serializers.ModelSerializer):
    city = CitySerializer(many=False, read_only=False)
    department = DepartmentSerializer(many=False, read_only=True)

    class Meta:
        model = Clinic
        fields = ['id', 'city', 'clinicName', 'department']


class ShieldingClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShieldingClassification
        fields = ['id', 'constant', 'classification', 'requiredShielding', 'requiredShieldingUnit']


class RoomSerializer(serializers.ModelSerializer):
    clinic = ClinicSerializer(many=False, read_only=True)
    shieldingClassification = ShieldingClassificationSerializer(many=False, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'clinic', 'room', 'roomWidth', 'roomLength', 'modalityType',
                  'shielding', 'shieldingClassification', 'shieldingClassificationDate',
                  'shieldingClassificationSignature', 'shieldingClassificationComment',
                  'drawing']
