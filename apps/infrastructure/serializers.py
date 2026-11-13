from rest_framework import serializers
from apps.infrastructure.models import Infrastructure, River, Dam, Canal, Bridge

class InfrastructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Infrastructure
        fields = '__all__'

class RiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = River
        fields = '__all__'

class DamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dam
        fields = '__all__'

class BridgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bridge
        fields = '__all__'
