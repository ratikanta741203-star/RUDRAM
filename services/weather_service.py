"""
Weather Service Adapter Layer
Seamlessly wraps OpenMeteoService and provides hydrological weather ingestion.
"""
from services.open_meteo import open_meteo_service, OpenMeteoService, WMO_WEATHER_CODES, get_weather_description

class WeatherService:
    def __init__(self):
        self.client = open_meteo_service

    def get_current_and_forecast(self, lat=20.2961, lon=85.8245):
        """
        Retrieves weather telemetry from Open-Meteo with fallback.
        """
        res = self.client.fetch_weather_data(latitude=lat, longitude=lon)
        if not res.get('success'):
            return self.client._get_demo_weather(lat, lon)

        curr = res.get('current', {})
        hourly = res.get('hourly', {})
        daily = res.get('daily', {})

        return {
            'status': 'LIVE' if not res.get('is_demo') else 'DEMO',
            'source': res.get('source', 'Open-Meteo'),
            'is_demo': res.get('is_demo', False),
            'last_updated': res.get('last_updated'),
            'response_time_ms': res.get('response_time_ms', 10.0),
            'coordinates': {'lat': lat, 'lon': lon},
            'current': {
                'temperature_c': curr.get('temperature', 28.4),
                'humidity_pct': curr.get('humidity', 84),
                'rainfall_current_mm': curr.get('rainfall', 0.0),
                'wind_speed_kmh': curr.get('wind_speed', 20.0),
                'wind_direction_deg': curr.get('wind_direction', 140),
                'surface_pressure_hpa': 1004.2,
                'condition': curr.get('condition', 'Clear Sky'),
                'weather_code': curr.get('weather_code', 0)
            },
            'forecast_24h_rainfall_mm': curr.get('total_24h_rainfall_mm', sum(hourly.get('precipitation', [0.0]*24)[:24])),
            'hourly': {
                'time': hourly.get('time', []),
                'precipitation': hourly.get('precipitation', []),
                'temperature': hourly.get('temperature', []),
                'wind_speed': hourly.get('wind_speed', [])
            },
            'daily': {
                'time': daily.get('time', []),
                'precipitation_sum': daily.get('precipitation_sum', []),
                'temp_max': daily.get('temperature_max', []),
                'temp_min': daily.get('temperature_min', [])
            }
        }

    def _map_weather_code(self, code):
        return get_weather_description(code)


weather_service = WeatherService()
