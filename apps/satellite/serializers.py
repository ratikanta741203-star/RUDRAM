from rest_framework import serializers
from apps.satellite.models import SatelliteAnalysis, DamageZone

class DamageZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamageZone
        fields = '__all__'

class SatelliteAnalysisSerializer(serializers.ModelSerializer):
    damage_zones = DamageZoneSerializer(many=True, read_only=True)

    class Meta:
        model = SatelliteAnalysis
        fields = '__all__'
