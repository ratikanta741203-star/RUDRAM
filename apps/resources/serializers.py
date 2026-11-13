from rest_framework import serializers
from apps.resources.models import Resource, ResourceAllocation, RescueTeam

class ResourceSerializer(serializers.ModelSerializer):
    remaining_deficit = serializers.IntegerField(read_only=True)

    class Meta:
        model = Resource
        fields = '__all__'

class ResourceAllocationSerializer(serializers.ModelSerializer):
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    resource_unit = serializers.CharField(source='resource.unit', read_only=True)

    class Meta:
        model = ResourceAllocation
        fields = '__all__'

class RescueTeamSerializer(serializers.ModelSerializer):
    team_type_display = serializers.CharField(source='get_team_type_display', read_only=True)

    class Meta:
        model = RescueTeam
        fields = '__all__'
