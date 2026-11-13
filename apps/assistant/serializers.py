from rest_framework import serializers
from apps.assistant.models import EmergencyRecommendation

class EmergencyRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyRecommendation
        fields = '__all__'
