import os
import time
import requests
import logging
from django.conf import settings
from apps.core.models import DataSourceStatus

logger = logging.getLogger(__name__)

class FirmsService:
    """
    NASA FIRMS (Fire Information for Resource Management System) Adapter.
    Uses VIIRS / MODIS thermal anomaly telemetry.
    """
    def __init__(self):
        self.endpoint = getattr(settings, 'FIRMS_URL', 'https://firms.modaps.eosdis.nasa.gov/api/area')
        self.api_key = getattr(settings, 'FIRMS_API_KEY', '') or os.getenv('FIRMS_API_KEY', '')

    def get_fire_hotspots(self, lat=20.2961, lon=85.8245, radius_deg=0.5):
        """
        Retrieves thermal anomalies / active fire hotspots for a given bounding box.
        If FIRMS_API_KEY is configured, performs a live query; otherwise serves calibrated DEMO dataset.
        """
        if self.api_key:
            start_time = time.time()
            try:
                # Bounding box: south, west, north, east
                s = round(lat - radius_deg, 3)
                w = round(lon - radius_deg, 3)
                n = round(lat + radius_deg, 3)
                e = round(lon + radius_deg, 3)
                bbox_str = f"{w},{s},{e},{n}"
                url = f"{self.endpoint}/csv/{self.api_key}/VIIRS_SNPP_NRT/{bbox_str}/1"

                res = requests.get(url, timeout=5)
                elapsed_ms = round((time.time() - start_time) * 1000, 1)

                if res.status_code == 200 and 'latitude' in res.text:
                    lines = res.text.strip().split('\n')
                    header = lines[0].split(',')
                    hotspots = []
                    for line in lines[1:]:
                        parts = line.split(',')
                        if len(parts) >= 6:
                            try:
                                h_lat = float(parts[0])
                                h_lon = float(parts[1])
                                frp = float(parts[5]) if len(parts) > 5 and parts[5] else 10.0
                                hotspots.append({
                                    'lat': h_lat,
                                    'lon': h_lon,
                                    'confidence': 85,
                                    'frp_mw': frp,
                                    'satellite': 'VIIRS-SNPP (Live)',
                                    'acq_time': parts[2] if len(parts) > 2 else 'Live',
                                    'type': 'Thermal Anomaly / Active Fire'
                                })
                            except ValueError:
                                continue

                    DataSourceStatus.objects.update_or_create(
                        source_name='nasa_firms',
                        defaults={
                            'display_name': 'NASA FIRMS Fire Hotspots',
                            'category': 'Thermal Remote Sensing',
                            'status': 'CONNECTED',
                            'is_live': True,
                            'endpoint_url': self.endpoint,
                            'response_time_ms': elapsed_ms,
                            'error_message': ''
                        }
                    )

                    return {
                        'status': 'LIVE',
                        'source': 'NASA FIRMS VIIRS Active Fire Detection (Live Telemetry)',
                        'is_demo': False,
                        'hotspots': hotspots
                    }
            except Exception as err:
                logger.warning(f"NASA FIRMS query exception: {err}")

        is_demo_mode = getattr(settings, 'DEMO_MODE', False)
        if not is_demo_mode:
            err_msg = 'FIRMS_API_KEY not configured in environment.' if not self.api_key else 'NASA FIRMS live server unreachable.'
            DataSourceStatus.objects.update_or_create(
                source_name='nasa_firms',
                defaults={
                    'display_name': 'NASA FIRMS Fire Hotspots',
                    'category': 'Thermal Remote Sensing',
                    'status': 'CONFIGURATION_REQUIRED' if not self.api_key else 'UNAVAILABLE',
                    'is_live': False,
                    'endpoint_url': self.endpoint,
                    'error_message': err_msg
                }
            )
            return {
                'status': 'CONFIGURATION_REQUIRED' if not self.api_key else 'UNAVAILABLE',
                'source': 'NASA FIRMS VIIRS Active Fire Detection',
                'is_demo': False,
                'hotspots': [],
                'message': err_msg
            }

        # Fallback to calibrated simulation only when DEMO_MODE is True
        DataSourceStatus.objects.update_or_create(
            source_name='nasa_firms',
            defaults={
                'display_name': 'NASA FIRMS Fire Hotspots',
                'category': 'Thermal Remote Sensing',
                'status': 'DEMO',
                'is_live': False,
                'endpoint_url': self.endpoint,
                'error_message': 'No FIRMS API Key supplied. Displaying calibrated simulation in DEMO_MODE.'
            }
        )

        return {
            'status': 'DEMO',
            'source': 'NASA FIRMS VIIRS/MODIS Active Fire Detection (Simulated DEMO)',
            'is_demo': True,
            'hotspots': [
                {'lat': lat + 0.12, 'lon': lon - 0.08, 'confidence': 88, 'frp_mw': 24.5, 'satellite': 'VIIRS-NOAA20', 'acq_time': '10:45 UTC', 'type': 'Forest Biomass Burning'},
                {'lat': lat + 0.18, 'lon': lon + 0.05, 'confidence': 94, 'frp_mw': 45.2, 'satellite': 'MODIS-Aqua', 'acq_time': '11:10 UTC', 'type': 'Agricultural Residue Burn'},
                {'lat': lat - 0.09, 'lon': lon + 0.14, 'confidence': 72, 'frp_mw': 14.1, 'satellite': 'VIIRS-SNPP', 'acq_time': '09:30 UTC', 'type': 'Urban Waste Heat Hotspot'},
            ]
        }

firms_service = FirmsService()
