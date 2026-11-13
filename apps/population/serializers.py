from rest_framework import serializers
from apps.population.models import PopulationExposure

class PopulationExposureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopulationExposure
        fields = '__all__'
