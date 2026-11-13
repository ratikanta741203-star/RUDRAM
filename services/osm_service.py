import requests
import json
import time
from django.conf import settings
from apps.core.models import DataSourceStatus

class OsmService:
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"

    def query_infrastructure(self, lat=20.2961, lon=85.8245, radius_m=5000):
        """
        Queries OpenStreetMap via Overpass API for emergency facilities.
        """
        start = time.time()
        overpass_query = f"""
        [out:json][timeout:10];
        (
          node["amenity"="hospital"](around:{radius_m},{lat},{lon});
          node["amenity"="shelter"](around:{radius_m},{lat},{lon});
          node["amenity"="fire_station"](around:{radius_m},{lat},{lon});
          node["amenity"="police"](around:{radius_m},{lat},{lon});
          node["amenity"="school"](around:{radius_m},{lat},{lon});
        );
        out body 25;
        """
        try:
            res = requests.post(self.overpass_url, data={'data': overpass_query}, timeout=5)
            elapsed_ms = round((time.time() - start) * 1000, 1)

            if res.status_code == 200:
                data = res.json()
                elements = data.get('elements', [])
                results = []
                for el in elements:
                    tags = el.get('tags', {})
                    results.append({
                        'id': el.get('id'),
                        'name': tags.get('name', f"Facility #{el.get('id')}"),
                        'type': tags.get('amenity', 'general'),
                        'lat': el.get('lat'),
                        'lon': el.get('lon'),
                        'operator': tags.get('operator', ''),
                        'phone': tags.get('phone', tags.get('contact:phone', '112 / 1077'))
                    })

                DataSourceStatus.objects.update_or_create(
                    source_name='overpass',
                    defaults={
                        'display_name': 'OpenStreetMap Overpass API',
                        'category': 'GIS & Infrastructure',
                        'status': 'CONNECTED',
                        'is_live': True,
                        'endpoint_url': self.overpass_url,
                        'response_time_ms': elapsed_ms,
                        'error_message': ''
                    }
                )

                return {'status': 'LIVE', 'count': len(results), 'features': results}
        except Exception as e:
            DataSourceStatus.objects.update_or_create(
                source_name='overpass',
                defaults={
                    'display_name': 'OpenStreetMap Overpass API',
                    'category': 'GIS & Infrastructure',
                    'status': 'TEMPORARILY_UNAVAILABLE',
                    'is_live': False,
                    'endpoint_url': self.overpass_url,
                    'error_message': str(e)
                }
            )

        is_demo_mode = getattr(settings, 'DEMO_MODE', False)
        if not is_demo_mode:
            return {
                'status': 'UNAVAILABLE',
                'count': 0,
                'features': [],
                'is_demo': False,
                'message': 'OpenStreetMap Overpass service temporarily unavailable.'
            }

        return self._get_demo_infrastructure(lat, lon)

    def _get_demo_infrastructure(self, lat, lon):
        return {
            'status': 'DEMO',
            'count': 12,
            'features': [
                {'name': 'AIIMS Bhubaneswar Hospital', 'type': 'hospital', 'lat': lat - 0.035, 'lon': lon - 0.025, 'phone': '0674-2476789'},
                {'name': 'Capital Hospital Unit 6', 'type': 'hospital', 'lat': lat + 0.015, 'lon': lon - 0.012, 'phone': '0674-2391983'},
                {'name': 'SUM Ultimate Medicare', 'type': 'hospital', 'lat': lat + 0.045, 'lon': lon + 0.035, 'phone': '0674-2386200'},
                {'name': 'Odisha Fire & Disaster Academy', 'type': 'fire_station', 'lat': lat - 0.02, 'lon': lon + 0.02, 'phone': '101'},
                {'name': 'Kalpana Fire Station', 'type': 'fire_station', 'lat': lat + 0.01, 'lon': lon + 0.04, 'phone': '101'},
                {'name': 'Khandagiri Police Station', 'type': 'police', 'lat': lat - 0.015, 'lon': lon - 0.03, 'phone': '112'},
                {'name': 'Saheed Nagar Police Station', 'type': 'police', 'lat': lat + 0.02, 'lon': lon + 0.03, 'phone': '112'},
                {'name': 'Buxi Jagabandhu Bidyadhar College Shelter', 'type': 'shelter', 'lat': lat + 0.01, 'lon': lon + 0.02, 'phone': '1077'},
                {'name': 'Kharavela Nagar Multipurpose Cyclone Shelter', 'type': 'shelter', 'lat': lat + 0.025, 'lon': lon + 0.015, 'phone': '1077'},
                {'name': 'Patia Higher Secondary High School', 'type': 'school', 'lat': lat + 0.07, 'lon': lon + 0.01, 'phone': '0674-2740001'},
            ]
        }

osm_service = OsmService()
