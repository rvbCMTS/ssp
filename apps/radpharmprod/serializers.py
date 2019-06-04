from rest_framework import serializers

from .models import Production


class ProductionSerializer(serializers.ModelSerializer):
    count_patients = serializers.IntegerField(read_only=True)

    class Meta:
        model = Production
        fields = ('id', 'datum', 'activity_mbq', 'batch', 'signature', 'radiopharmaceutical', 'volume_ml',
                  'count_patients')
        depth = 1
