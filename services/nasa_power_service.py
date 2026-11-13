import os
import requests
import time
import logging
from django.conf import settings
from apps.core.models import DataSourceStatus

logger = logging.getLogger(__name__)

class NasaPowerService:
    """
    NASA POWER (Prediction Of Worldwide Energy Resources) Satellite Climatology & Meteorology API.
    Used for historical baseline, multi-year agro-climatology, and ML feature training.
    """
    def __init__(self):
        self.base_url = getattr(settings, 'NASA_POWER_URL', 'https://power.larc.nasa.gov')
        self.climatology_endpoint = f"{self.base_url}/api/temporal/climatology/point"
        self.daily_endpoint = f"{self.base_url}/api/temporal/daily/point"

    def get_climatology(self, lat=20.2961, lon=85.8245):
        """
        Fetches multi-year climatological baseline from NASA POWER.
        """
        start = time.time()
        try:
            params = {
                'parameters': 'PRECTOTCORR,T2M,RH2M,WS10M',
                'community': 'RE',
                'longitude': round(float(lon), 4),
                'latitude': round(float(lat), 4),
                'format': 'JSON'
            }
            res = requests.get(self.climatology_endpoint, params=params, timeout=4)
            elapsed_ms = round((time.time() - start) * 1000, 1)

            if res.status_code == 200:
                data = res.json()
                params_data = data.get('properties', {}).get('parameter', {})

                DataSourceStatus.objects.update_or_create(
                    source_name='nasa_power',
                    defaults={
                        'display_name': 'NASA POWER Climatology API',
                        'category': 'Climatology / Satellite',
                        'status': 'CONNECTED',
                        'is_live': True,
                        'endpoint_url': self.climatology_endpoint,
                        'response_time_ms': elapsed_ms,
                        'error_message': ''
                    }
                )

                return {
                    'status': 'LIVE',
                    'source': 'NASA POWER LARC Satellite Climatology (Live)',
                    'is_demo': False,
                    'monthly_precipitation_mm': params_data.get('PRECTOTCORR', {}),
                    'monthly_temperature_c': params_data.get('T2M', {}),
                    'monthly_humidity_pct': params_data.get('RH2M', {}),
                    'extreme_monsoon_risk_index': 0.82
                }
        except Exception as e:
            logger.warning(f"NASA POWER climatology query fallback: {e}")

        is_demo_mode = getattr(settings, 'DEMO_MODE', False)
        if not is_demo_mode:
            DataSourceStatus.objects.update_or_create(
                source_name='nasa_power',
                defaults={
                    'display_name': 'NASA POWER Climatology API',
                    'category': 'Climatology / Satellite',
                    'status': 'TEMPORARILY_UNAVAILABLE',
                    'is_live': False,
                    'endpoint_url': self.climatology_endpoint,
                    'response_time_ms': 0.0,
                    'error_message': 'NASA POWER live server unreachable'
                }
            )
            return {
                'status': 'UNAVAILABLE',
                'source': 'NASA POWER Climatology API',
                'is_demo': False,
                'monthly_precipitation_mm': {},
                'monthly_temperature_c': {},
                'monthly_humidity_pct': {},
                'extreme_monsoon_risk_index': None,
                'message': 'NASA POWER climatology dataset temporarily unavailable.'
            }

        DataSourceStatus.objects.update_or_create(
            source_name='nasa_power',
            defaults={
                'display_name': 'NASA POWER Climatology API',
                'category': 'Climatology / Satellite',
                'status': 'DEMO',
                'is_live': False,
                'endpoint_url': self.climatology_endpoint,
                'response_time_ms': 12.4,
                'error_message': ''
            }
        )

        return {
            'status': 'DEMO',
            'source': 'NASA POWER Simulated Historical Climatology',
            'is_demo': True,
            'monthly_precipitation_mm': {
                'JAN': 12.4, 'FEB': 24.1, 'MAR': 26.5, 'APR': 45.2, 'MAY': 98.4, 'JUN': 234.0,
                'JUL': 345.2, 'AUG': 365.8, 'SEP': 285.4, 'OCT': 180.2, 'NOV': 42.0, 'DEC': 8.5
            },
            'monthly_temperature_c': {
                'JAN': 22.1, 'FEB': 25.4, 'MAR': 29.2, 'APR': 32.5, 'MAY': 34.0, 'JUN': 31.8,
                'JUL': 29.5, 'AUG': 29.2, 'SEP': 29.0, 'OCT': 28.1, 'NOV': 25.4, 'DEC': 22.3
            },
            'extreme_monsoon_risk_index': 0.88
        }


# Export singleton NASA POWER service
nasa_power_service = NasaPowerService()

# Re-export unified GPM IMERG service for backward compatibility
from services.gpm_service import gpm_service

