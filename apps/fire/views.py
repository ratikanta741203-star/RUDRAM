from rest_framework.views import APIView
from rest_framework.response import Response
from services.firms_service import firms_service
from apps.fire.models import FireHotspot

class FireHotspotsAPIView(APIView):
    """
    GET /api/fire/hotspots/?lat=...&lon=...
    """
    def get(self, request):
        lat = float(request.query_params.get('lat', 20.2961))
        lon = float(request.query_params.get('lon', 85.8245))
        data = firms_service.get_fire_hotspots(lat, lon)
        return Response(data)
