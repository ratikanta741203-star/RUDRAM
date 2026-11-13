from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.population.models import PopulationExposure
from apps.population.serializers import PopulationExposureSerializer

def population_view(request):
    zones = PopulationExposure.objects.all()
    has_zone_data = zones.exists()
    total_pop = sum(z.total_population for z in zones)
    exposed_pop = sum(z.exposed_population for z in zones)
    vulnerable_pop = sum(z.vulnerable_population for z in zones)
    critical_pop = sum(z.critical_risk_population for z in zones)

    context = {
        'zones': zones,
        'has_zone_data': has_zone_data,
        'total_pop': total_pop,
        'exposed_pop': exposed_pop,
        'vulnerable_pop': vulnerable_pop,
        'critical_pop': critical_pop,
        'exposure_percentage': round(exposed_pop / total_pop * 100, 1) if total_pop else 0,
        'shelter_deficit': sum(z.shelter_deficit_count for z in zones),
        'population_chart_data': [
            max(total_pop - min(exposed_pop, total_pop), 0),
            min(max(exposed_pop, 0), max(total_pop, 0)),
        ],
        'page_title': 'Population Vulnerability & Exposure Analytics'
    }
    return render(request, 'population/exposure.html', context)

class PopulationExposureAPIView(APIView):
    """
    GET /api/population/exposure/
    """
    def get(self, request):
        zones = PopulationExposure.objects.all()
        serializer = PopulationExposureSerializer(zones, many=True)
        return Response({
            'success': True,
            'source': 'WorldPop / High-Resolution Population Density Layer',
            'is_demo': True,
            'zones': serializer.data
        })
