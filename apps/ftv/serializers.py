from rest_framework import serializers
from .models import Machine
from apps.radiation_shielding.models import Room


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        depth = 1
        fields = '__all__'


class MachineSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Machine
        depth = 1
        fields = ('machine_name', 'inventory_system_id', 'model', 'room', 'machine_type', 'installed_date', 'in_use')
