from rest_framework import serializers
from apps.weather.models import WeatherObservation, RainfallObservation

class WeatherObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherObservation
        fields = '__all__'

class RainfallObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RainfallObservation
        fields = '__all__'
