from rest_framework import serializers
from apps.disasters.models import Disaster, DisasterTimeline

class DisasterTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisasterTimeline
        fields = '__all__'

class DisasterSerializer(serializers.ModelSerializer):
    timeline = DisasterTimelineSerializer(many=True, read_only=True)

    class Meta:
        model = Disaster
        fields = '__all__'
