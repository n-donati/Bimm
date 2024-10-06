from rest_framework import serializers
from app.models import Line

class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ['time', 'amplitude']