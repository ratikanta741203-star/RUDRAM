from rest_framework import serializers
from apps.risk.models import RiskPrediction, RiskZone

class RiskPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskPrediction
        fields = '__all__'

class RiskZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskZone
        fields = '__all__'
