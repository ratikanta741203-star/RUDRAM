from rest_framework import serializers
from apps.evacuation.models import EvacuationRoute

class EvacuationRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvacuationRoute
        fields = '__all__'
