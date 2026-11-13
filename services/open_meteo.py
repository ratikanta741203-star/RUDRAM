import time
import logging
import requests
from django.conf import settings
from django.core.cache import cache
from apps.core.models import DataSourceStatus

logger = logging.getLogger(__name__)

# WMO Weather Code to Human-Readable Description (Official Open-Meteo WMO Table)
WMO_WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    56: "Light Freezing Drizzle",
    57: "Dense Freezing Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Slight Snow Fall",
    73: "Moderate Snow Fall",
    75: "Heavy Snow Fall",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}

def get_weather_description(code: int) -> str:
    """Converts an Open-Meteo WMO weather code to a human-readable string."""
    return WMO_WEATHER_CODES.get(code, "Variable Weather")


class OpenMeteoService:
    """
    Open-Meteo Weather Forecast API Service Adapter.
    Endpoint: https://api.open-meteo.com/v1/forecast
    Free public API: does NOT require an API key.
    """
    REQUEST_TIMEOUT = (5, 10)  # (connect timeout, read timeout)
    CACHE_TTL = 300      # 5 minutes in-memory cache

    @property
    def base_url(self) -> str:
        base = getattr(settings, 'OPEN_METEO_URL', 'https://api.open-meteo.com/v1/forecast').rstrip('/')
        if not base.endswith('/v1/forecast'):
            return f"{base}/v1/forecast"
        return base

    def get_current_weather(self, latitude: float, longitude: float) -> dict:
        """
        Fetches current meteorological variables for a specific coordinate pair.
        Uses max 2 short retries with exponential backoff and timeout=(5, 10).
        """
        self._validate_coordinates(latitude, longitude)

        cache_key = f"open_meteo_curr_{round(float(latitude), 4)}_{round(float(longitude), 4)}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        params = {
            'latitude': round(float(latitude), 4),
            'longitude': round(float(longitude), 4),
            'current': 'temperature_2m,relative_humidity_2m,precipitation,rain,showers,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m',
            'timezone': 'auto'
        }

        max_retries = 2
        last_error = ""

        for attempt in range(max_retries + 1):
            start_time = time.time()
            try:
                response = requests.get(self.base_url, params=params, timeout=self.REQUEST_TIMEOUT)
                elapsed_ms = round((time.time() - start_time) * 1000, 1)

                if response.status_code == 200:
                    raw_data = response.json()
                    current_raw = raw_data.get('current', {})
                    wcode = current_raw.get('weather_code', 0)
                    condition = get_weather_description(wcode)

                    self._update_data_source_status('CONNECTED', True, elapsed_ms, '')

                    result = {
                        'success': True,
                        'source': 'Open-Meteo',
                        'status': 'connected',
                        'is_demo': False,
                        'last_updated': current_raw.get('time', time.strftime('%Y-%m-%dT%H:%M')),
                        'response_time_ms': elapsed_ms,
                        'location': {
                            'latitude': float(latitude),
                            'longitude': float(longitude),
                            'elevation': raw_data.get('elevation', 0.0),
                            'timezone': raw_data.get('timezone', 'auto')
                        },
                        'current': {
                            'temperature': current_raw.get('temperature_2m', 0.0),
                            'humidity': current_raw.get('relative_humidity_2m', 0),
                            'rainfall': current_raw.get('precipitation', 0.0),
                            'rain': current_raw.get('rain', 0.0),
                            'showers': current_raw.get('showers', 0.0),
                            'wind_speed': current_raw.get('wind_speed_10m', 0.0),
                            'wind_direction': current_raw.get('wind_direction_10m', 0),
                            'wind_gusts': current_raw.get('wind_gusts_10m', 0.0),
                            'weather_code': wcode,
                            'condition': condition
                        }
                    }

                    cache.set(cache_key, result, self.CACHE_TTL)
                    return result
                else:
                    last_error = f"HTTP {response.status_code}"
                    logger.warning(f"Open-Meteo current API status {response.status_code} for ({latitude}, {longitude}) on attempt {attempt + 1}")
            except requests.exceptions.RequestException as req_err:
                last_error = str(req_err)
                logger.warning(f"Open-Meteo connection error for ({latitude}, {longitude}) on attempt {attempt + 1}: {req_err}")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Open-Meteo processing error for ({latitude}, {longitude}) on attempt {attempt + 1}: {e}")

            if attempt < max_retries:
                time.sleep(0.2 * (2 ** attempt))

        return self._handle_failure(latitude, longitude, last_error)

    def get_batch_weather(self, locations_list: list) -> list:
        """
        Fetches current weather for multiple location coordinates in a SINGLE batched Open-Meteo HTTP request.
        Uses maximum 2 short retries with exponential backoff and timeout=(5, 10).
        Returns list of location objects populated with live Open-Meteo weather telemetry.
        """
        if not locations_list:
            return []

        lats_str = ','.join(str(round(float(x.get('lat', x.get('latitude', 0))), 4)) for x in locations_list)
        lons_str = ','.join(str(round(float(x.get('lon', x.get('longitude', 0))), 4)) for x in locations_list)

        params = {
            'latitude': lats_str,
            'longitude': lons_str,
            'current': 'temperature_2m,relative_humidity_2m,precipitation,rain,showers,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m',
            'timezone': 'auto'
        }

        # Short retries: Max 2 retries (3 attempts total) with short backoff
        max_retries = 2
        raw_results = None
        start_time = time.time()

        for attempt in range(max_retries + 1):
            try:
                res = requests.get(self.base_url, params=params, timeout=(5, 10))
                if res.status_code == 200:
                    raw_results = res.json()
                    elapsed_ms = round((time.time() - start_time) * 1000, 1)
                    self._update_data_source_status('CONNECTED', True, elapsed_ms, '')
                    break
                else:
                    logger.warning(f"Open-Meteo batch status {res.status_code} on attempt {attempt + 1}")
            except requests.exceptions.RequestException as err:
                logger.warning(f"Open-Meteo batch connection attempt {attempt + 1} failed: {err}")

            if attempt < max_retries:
                time.sleep(0.2 * (2 ** attempt))

        results = []
        if isinstance(raw_results, dict):
            raw_results = [raw_results]
        elif not isinstance(raw_results, list):
            raw_results = []

        for i, loc in enumerate(locations_list):
            item = raw_results[i] if i < len(raw_results) and isinstance(raw_results[i], dict) else {}
            curr = item.get('current', {})
            temp = curr.get('temperature_2m')
            wcode = curr.get('weather_code')

            is_valid = temp is not None and wcode is not None
            loc_name = loc.get('name', loc.get('city', 'Unknown'))
            lat_val = float(loc.get('lat', loc.get('latitude', 0.0)))
            lon_val = float(loc.get('lon', loc.get('longitude', 0.0)))

            if is_valid:
                cond = get_weather_description(wcode)
                rain_val = float(curr.get('precipitation', 0.0) or 0.0)
                wind_val = float(curr.get('wind_speed_10m', 0.0) or 0.0)
                humid_val = float(curr.get('relative_humidity_2m', 0) or 0)

                # Live risk score calculation using meteorological parameters
                risk_score = 15.0
                if rain_val > 0:
                    risk_score += min(rain_val * 6.0, 50.0)
                if wind_val > 15.0:
                    risk_score += min((wind_val - 15.0) * 1.5, 20.0)
                if wcode in [61, 63, 65, 67, 80, 81, 82]:
                    risk_score += 15.0
                elif wcode in [95, 96, 99]:
                    risk_score += 25.0

                risk_score = min(max(round(risk_score, 1), 5.0), 98.0)

                if risk_score >= 75.0:
                    risk_level = 'CRITICAL'
                elif risk_score >= 60.0:
                    risk_level = 'HIGH'
                elif risk_score >= 40.0:
                    risk_level = 'MODERATE'
                else:
                    risk_level = 'LOW'

                results.append({
                    'name': loc_name,
                    'city': loc_name,
                    'code': loc.get('code', ''),
                    'state': loc.get('state', ''),
                    'capital': loc.get('capital', ''),
                    'type': loc.get('type', 'location'),
                    'latitude': lat_val,
                    'longitude': lon_val,
                    'lat': lat_val,
                    'lon': lon_val,
                    'zoom': loc.get('zoom', 7),
                    'temperature': temp,
                    'temp': temp,
                    'rainfall': rain_val,
                    'humidity': humid_val,
                    'wind_speed': wind_val,
                    'weather_code': wcode,
                    'condition': cond,
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'is_available': True,
                    'is_demo': False
                })
            else:
                # Live weather unavailable -> Never return fake numbers!
                results.append({
                    'name': loc_name,
                    'city': loc_name,
                    'code': loc.get('code', ''),
                    'state': loc.get('state', ''),
                    'capital': loc.get('capital', ''),
                    'type': loc.get('type', 'location'),
                    'latitude': lat_val,
                    'longitude': lon_val,
                    'lat': lat_val,
                    'lon': lon_val,
                    'zoom': loc.get('zoom', 7),
                    'temperature': None,
                    'temp': None,
                    'rainfall': None,
                    'humidity': None,
                    'wind_speed': None,
                    'weather_code': None,
                    'condition': 'Live weather unavailable',
                    'risk_score': None,
                    'risk_level': 'UNAVAILABLE',
                    'is_available': False,
                    'is_demo': False
                })

        return results

    def get_forecast(self, latitude: float, longitude: float, forecast_days: int = 7) -> dict:
        """
        Fetches hourly and daily meteorological forecasts from Open-Meteo.
        """
        self._validate_coordinates(latitude, longitude)
        days = self._validate_forecast_days(forecast_days)

        cache_key = f"open_meteo_fore_{round(latitude, 2)}_{round(longitude, 2)}_{days}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        params = {
            'latitude': round(float(latitude), 4),
            'longitude': round(float(longitude), 4),
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,rain,showers,wind_speed_10m,wind_direction_10m,weather_code',
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,wind_speed_10m_max',
            'forecast_days': int(days),
            'timezone': 'auto'
        }

        start_time = time.time()
        try:
            response = requests.get(self.base_url, params=params, timeout=self.REQUEST_TIMEOUT)
            elapsed_ms = round((time.time() - start_time) * 1000, 1)

            if response.status_code == 200:
                raw_data = response.json()
                hourly_raw = raw_data.get('hourly', {})
                daily_raw = raw_data.get('daily', {})

                self._update_data_source_status('CONNECTED', True, elapsed_ms, '')

                hourly_times = hourly_raw.get('time', [])
                hourly_precip = hourly_raw.get('precipitation', [])
                hourly_temp = hourly_raw.get('temperature_2m', [])
                hourly_wind = hourly_raw.get('wind_speed_10m', [])

                result = {
                    'success': True,
                    'source': 'Open-Meteo',
                    'status': 'connected',
                    'is_demo': False,
                    'last_updated': time.strftime('%Y-%m-%dT%H:%M'),
                    'response_time_ms': elapsed_ms,
                    'location': {
                        'latitude': float(latitude),
                        'longitude': float(longitude),
                        'elevation': raw_data.get('elevation', 0.0),
                        'timezone': raw_data.get('timezone', 'auto')
                    },
                    'hourly': {
                        'time': hourly_times,
                        'temperature': hourly_temp,
                        'relative_humidity': hourly_raw.get('relative_humidity_2m', []),
                        'precipitation_probability': hourly_raw.get('precipitation_probability', []),
                        'precipitation': hourly_precip,
                        'rain': hourly_raw.get('rain', []),
                        'showers': hourly_raw.get('showers', []),
                        'wind_speed': hourly_wind,
                        'wind_direction': hourly_raw.get('wind_direction_10m', []),
                        'weather_code': hourly_raw.get('weather_code', [])
                    },
                    'daily': {
                        'time': daily_raw.get('time', [])[:days],
                        'temperature_max': daily_raw.get('temperature_2m_max', [])[:days],
                        'temperature_min': daily_raw.get('temperature_2m_min', [])[:days],
                        'precipitation_sum': daily_raw.get('precipitation_sum', [])[:days],
                        'rain_sum': daily_raw.get('rain_sum', [])[:days],
                        'wind_speed_max': daily_raw.get('wind_speed_10m_max', [])[:days]
                    }
                }

                cache.set(cache_key, result, self.CACHE_TTL)
                return result
            else:
                logger.warning(f"Open-Meteo forecast API status {response.status_code} for ({latitude}, {longitude}): {response.text}")
                return self._handle_failure(latitude, longitude, f"HTTP {response.status_code}", upstream_status=response.status_code)

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Open-Meteo forecast connection error for ({latitude}, {longitude}): {req_err}")
            return self._handle_failure(latitude, longitude, str(req_err))
        except Exception as e:
            logger.error(f"Open-Meteo forecast processing error for ({latitude}, {longitude}): {e}")
            return self._handle_failure(latitude, longitude, str(e))

    def fetch_weather_data(self, latitude: float, longitude: float, forecast_days: int = 7) -> dict:
        """
        Unified method fetching both current and forecast data from Open-Meteo.
        """
        curr_res = self.get_current_weather(latitude, longitude)
        fore_res = self.get_forecast(latitude, longitude, forecast_days)

        if not curr_res.get('success') and not fore_res.get('success'):
            if getattr(settings, 'DEMO_MODE', False):
                return self._get_demo_weather(latitude, longitude)
            return curr_res

        is_demo = curr_res.get('is_demo', False) or fore_res.get('is_demo', False)
        source = curr_res.get('source', 'Open-Meteo')
        last_updated = curr_res.get('last_updated', time.strftime('%Y-%m-%dT%H:%M'))

        hourly = fore_res.get('hourly', {})
        daily = fore_res.get('daily', {})
        current = curr_res.get('current', {})

        # Compute 24h total rainfall from hourly precipitation if available
        precips = hourly.get('precipitation', [])[:24]
        total_24h_rainfall = round(sum(precips), 1) if precips else current.get('rainfall', 0.0)
        current['total_24h_rainfall_mm'] = total_24h_rainfall

        return {
            'success': True,
            'source': source,
            'status': 'connected',
            'is_demo': is_demo,
            'last_updated': last_updated,
            'location': curr_res.get('location', {'latitude': float(latitude), 'longitude': float(longitude)}),
            'current': current,
            'hourly': hourly,
            'daily': daily
        }

    def _validate_coordinates(self, latitude: float, longitude: float):
        if not isinstance(latitude, (int, float)) or not (-90.0 <= float(latitude) <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90 degrees. Given: {latitude}")
        if not isinstance(longitude, (int, float)) or not (-180.0 <= float(longitude) <= 180.0):
            raise ValueError(f"Longitude must be between -180 and 180 degrees. Given: {longitude}")

    def _validate_forecast_days(self, forecast_days) -> int:
        try:
            days = int(forecast_days)
        except (ValueError, TypeError):
            raise ValueError("forecast_days must be an integer.")
        if not (1 <= days <= 16):
            raise ValueError(f"forecast_days must be between 1 and 16. Given: {days}")
        return days

    def _update_data_source_status(self, status_val, is_live_val, response_time, err_msg):
        try:
            DataSourceStatus.objects.update_or_create(
                source_name='open_meteo',
                defaults={
                    'display_name': 'Open-Meteo Weather Forecast API',
                    'category': 'Meteorological',
                    'status': status_val,
                    'is_live': is_live_val,
                    'endpoint_url': self.base_url,
                    'response_time_ms': response_time,
                    'error_message': err_msg
                }
            )
        except Exception:
            pass

    def _handle_failure(self, latitude: float, longitude: float, error_detail: str, upstream_status: int = 502) -> dict:
        """Handles API failure according to DEMO_MODE configuration."""
        self._update_data_source_status('TEMPORARILY_UNAVAILABLE', False, 0.0, error_detail)

        is_demo_mode = getattr(settings, 'DEMO_MODE', False)
        if is_demo_mode:
            return self._get_demo_weather(latitude, longitude)

        return {
            'success': False,
            'source': 'Open-Meteo',
            'status': 'temporarily_unavailable',
            'message': 'Open-Meteo weather service returned an invalid response.',
            'upstream_status': upstream_status,
            'error_detail': error_detail,
            'location': {'latitude': latitude, 'longitude': longitude}
        }

    def _get_demo_weather(self, latitude: float, longitude: float) -> dict:
        """Returns calibrated deterministic demo weather dataset from central demo store."""
        from demo.loader import get_demo_data_by_key
        w_demo = get_demo_data_by_key('weather', {})
        r_demo = get_demo_data_by_key('rainfall', {})
        return {
            'success': True,
            'source': 'RUDRAM Central Demo Dataset',
            'status': 'connected',
            'is_demo': True,
            'last_updated': time.strftime('%Y-%m-%dT%H:%M:00'),
            'response_time_ms': 5.0,
            'location': {
                'latitude': float(latitude),
                'longitude': float(longitude),
                'elevation': 24.0,
                'timezone': 'Asia/Kolkata'
            },
            'current': {
                'temperature': w_demo.get('temperature_c', 27.5),
                'humidity': w_demo.get('humidity_pct', 92.0),
                'rainfall': r_demo.get('rainfall_1h_mm', 28.5),
                'rain': 22.0,
                'showers': 6.5,
                'wind_speed': w_demo.get('wind_speed_kmh', 42.0),
                'wind_direction': 160,
                'wind_gusts': 55.0,
                'weather_code': 65,
                'condition': w_demo.get('weather_condition', 'Heavy Monsoon Precipitation'),
                'total_24h_rainfall_mm': r_demo.get('rainfall_24h_mm', 195.4)
            },
            'hourly': {
                'time': [f"{h:02d}:00" for h in range(24)],
                'temperature': [26.5, 26.2, 25.8, 25.5, 25.8, 26.4, 27.2, 28.0, 28.5, 28.2, 27.8, 27.4, 27.0, 26.8, 26.5, 26.2, 26.0, 25.8, 25.6, 25.5, 25.4, 25.3, 25.2, 25.0],
                'relative_humidity': [92, 94, 95, 96, 95, 93, 90, 88, 86, 88, 90, 91, 93, 94, 95, 95, 96, 96, 95, 94, 94, 93, 92, 92],
                'precipitation_probability': [85, 90, 95, 100, 95, 90, 85, 80, 75, 80, 85, 90, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35],
                'precipitation': [8.5, 12.0, 15.4, 22.1, 28.5, 34.0, 26.2, 19.5, 14.0, 9.8, 6.2, 4.0, 3.5, 5.0, 8.2, 11.4, 18.0, 22.5, 19.0, 14.5, 10.0, 7.5, 5.0, 3.2],
                'rain': [8.0, 11.5, 15.0, 21.5, 27.0, 32.0, 25.0, 18.5, 13.0, 9.0, 5.5, 3.5, 3.0, 4.5, 7.5, 10.5, 17.0, 21.0, 18.0, 13.5, 9.5, 7.0, 4.5, 3.0],
                'showers': [0.5, 0.5, 0.4, 0.6, 1.5, 2.0, 1.2, 1.0, 1.0, 0.8, 0.7, 0.5, 0.5, 0.5, 0.7, 0.9, 1.0, 1.5, 1.0, 1.0, 0.5, 0.5, 0.5, 0.2],
                'wind_speed': [18.0, 20.5, 22.0, 26.4, 31.0, 35.5, 32.0, 28.0, 24.5, 22.0, 20.0, 18.5, 19.0, 21.0, 23.5, 25.0, 28.0, 30.5, 27.0, 24.0, 21.5, 19.0, 18.0, 17.5],
                'wind_direction': [140, 145, 150, 155, 160, 165, 160, 155, 150, 145, 140, 135, 140, 145, 150, 155, 160, 165, 160, 155, 150, 145, 140, 135],
                'weather_code': [65]*24
            },
            'daily': {
                'time': ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
                'temperature_max': [29.0, 29.5, 30.5, 31.0, 32.5, 33.0, 33.5],
                'temperature_min': [24.5, 24.8, 25.0, 25.2, 25.8, 26.0, 26.2],
                'precipitation_sum': [186.4, 142.0, 95.5, 45.0, 22.0, 8.5, 2.0],
                'rain_sum': [175.0, 132.0, 88.0, 40.0, 18.0, 7.0, 1.5],
                'wind_speed_max': [42.0, 38.5, 32.0, 25.0, 20.0, 18.0, 15.0]
            }
        }


# Singleton service instance for standard importing
open_meteo_service = OpenMeteoService()
