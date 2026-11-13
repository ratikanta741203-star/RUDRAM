from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.shelters.models import Shelter
from services.google_maps_service import google_maps_service

@ensure_csrf_cookie
def evacuation_view(request):
    """
    Safe Evacuation View using Real Admin-Added Shelters & Live Google Routes.
    """
    shelters = Shelter.objects.all()
    shelters_data = [{
        'id': s.id,
        'name': s.name,
        'address': s.address,
        'latitude': float(s.latitude),
        'longitude': float(s.longitude),
        'total_capacity': s.total_capacity,
        'current_occupancy': s.current_occupancy,
        'available_capacity': s.available_capacity,
        'status': s.status
    } for s in shelters]

    context = {
        'shelters': shelters,
        'shelters_json': shelters_data,
        'page_title': 'Safe Evacuation & Dynamic Route Planner'
    }
    return render(request, 'evacuation/index.html', context)

class EvacuationRouteAPIView(APIView):
    """
    POST /api/evacuation/route/
    Calculates live routes between current GPS origin and selected Admin shelter destination via Google Routes API.
    """
    def post(self, request):
        try:
            start_lat = float(request.data.get('start_lat'))
            start_lon = float(request.data.get('start_lon'))
            end_lat = float(request.data.get('end_lat'))
            end_lon = float(request.data.get('end_lon'))
        except (TypeError, ValueError):
            return Response({
                'success': False,
                'message': 'Invalid origin or destination coordinates.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Compute live route using Google Maps / Routes API
        route_result = google_maps_service.compute_google_routes(start_lat, start_lon, end_lat, end_lon)

        if not route_result or route_result.get('status') == 'UNAVAILABLE':
            return Response({
                'success': False,
                'message': 'Unable to calculate route. Please try again.'
            }, status=status.HTTP_200_OK)

        return Response({
            'success': True,
            'result': route_result
        }, status=status.HTTP_200_OK)
