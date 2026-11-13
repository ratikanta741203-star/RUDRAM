from rest_framework import serializers
from apps.shelters.models import Shelter

class ShelterSerializer(serializers.ModelSerializer):
    available_capacity = serializers.IntegerField(read_only=True)
    occupancy_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Shelter
        fields = '__all__'
