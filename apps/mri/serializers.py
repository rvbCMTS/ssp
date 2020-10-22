from rest_framework import serializers

from .models import BookTitle


class BookTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookTitle
        fields = '__all__'
