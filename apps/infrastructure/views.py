from rest_framework.views import APIView
from rest_framework.response import Response
from apps.infrastructure.models import Infrastructure, River, Dam, Canal, Bridge
from apps.infrastructure.serializers import InfrastructureSerializer, RiverSerializer, DamSerializer, BridgeSerializer
from services.osm_service import osm_service

class InfrastructureListAPIView(APIView):
    """
    GET /api/infrastructure/?lat=...&lon=...
    """
    def get(self, request):
        lat = float(request.query_params.get('lat', 20.2961))
        lon = float(request.query_params.get('lon', 85.8245))
        
        # Local database assets
        db_infra = Infrastructure.objects.all()
        serializer = InfrastructureSerializer(db_infra, many=True)

        # Dynamic OSM query
        osm_data = osm_service.query_infrastructure(lat, lon)

        return Response({
            'success': True,
            'database_assets': serializer.data,
            'osm_live_assets': osm_data
        })

class WaterBodiesAPIView(APIView):
    """
    GET /api/infrastructure/water-bodies/
    """
    def get(self, request):
        rivers = River.objects.all()
        dams = Dam.objects.all()
        bridges = Bridge.objects.all()
        return Response({
            'success': True,
            'source': 'Central Water Commission (CWC) & State Irrigation Dept (Simulated Baseline)',
            'rivers': RiverSerializer(rivers, many=True).data,
            'dams': DamSerializer(dams, many=True).data,
            'bridges': BridgeSerializer(bridges, many=True).data
        })
