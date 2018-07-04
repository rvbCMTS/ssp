from rest_framework import serializers
from .models import Profession, Personnel, DosimeterPlacement, VendorDosimeterPlacement, Result, Deviation


class ProfessionSerializer(serializers.Serializer):

    class Meta:
        model = Profession


class AnonymousPersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personnel
        fields = ('id', 'profession')


class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personnel


class DosimeterPlacementSerializer(serializers.ModelSerializer):

    class Meta:
        model = DosimeterPlacement


class VendorDosimeterPlacementSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorDosimeterPlacement


class PersonnelDosimetryResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result


class DeviationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deviation
