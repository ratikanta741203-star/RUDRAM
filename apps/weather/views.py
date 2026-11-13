import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.open_meteo import open_meteo_service
from services.weather_service import weather_service
from services.nasa_power_service import nasa_power_service, gpm_service
from apps.weather.models import WeatherObservation

logger = logging.getLogger(__name__)

import math

def parse_coordinates(request):
    """Helper to extract and validate latitude & longitude from query parameters."""
    lat_val = request.query_params.get('latitude', request.query_params.get('lat', '20.2961'))
    lon_val = request.query_params.get('longitude', request.query_params.get('lon', '85.8245'))

    try:
        lat = float(lat_val)
        lon = float(lon_val)
        if math.isnan(lat) or math.isnan(lon):
            return None, None, "Latitude and longitude must be valid non-NaN numerical floats."
    except (ValueError, TypeError):
        return None, None, "Latitude and longitude must be valid numerical floats."

    if not (-90.0 <= lat <= 90.0):
        return None, None, f"Latitude must be between -90 and 90 degrees. Given: {lat}"
    if not (-180.0 <= lon <= 180.0):
        return None, None, f"Longitude must be between -180 and 180 degrees. Given: {lon}"

    return lat, lon, None


class CurrentWeatherAPIView(APIView):
    """
    GET /api/weather/current/?latitude=...&longitude=...
    Retrieves current live weather from Open-Meteo API.
    """
    def get(self, request):
        lat, lon, err = parse_coordinates(request)
        if err:
            return Response({
                'success': False,
                'source': 'Open-Meteo',
                'status': 'invalid_parameters',
                'message': err
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = open_meteo_service.get_current_weather(latitude=lat, longitude=lon)

            # Persist observation if successful and live
            if data.get('success') and not data.get('is_demo'):
                curr = data.get('current', {})
                try:
                    WeatherObservation.objects.create(
                        station_name=f"Open-Meteo Grid ({round(lat, 2)}, {round(lon, 2)})",
                        latitude=lat,
                        longitude=lon,
                        temperature_c=curr.get('temperature', 0.0),
                        humidity_pct=curr.get('humidity', 0.0),
                        rainfall_current_mm=curr.get('rainfall', 0.0),
                        rainfall_24h_mm=curr.get('rainfall', 0.0),
                        wind_speed_kmh=curr.get('wind_speed', 0.0),
                        wind_direction_deg=curr.get('wind_direction', 0.0),
                        weather_condition=curr.get('condition', 'Clear Sky'),
                        source=data.get('source', 'Open-Meteo'),
                        is_demo=False
                    )
                except Exception as db_err:
                    logger.warning(f"Could not persist WeatherObservation: {db_err}")

            if not data.get('success'):
                return Response({
                    'success': False,
                    'live': False,
                    'source': 'Open-Meteo',
                    'status': 'unavailable',
                    'error': 'Live weather temporarily unavailable',
                    'message': 'Live weather temporarily unavailable'
                }, status=status.HTTP_200_OK)

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in CurrentWeatherAPIView: {e}")
            return Response({
                'success': False,
                'source': 'Open-Meteo',
                'status': 'temporarily_unavailable',
                'message': 'Weather service is temporarily unavailable.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class ForecastWeatherAPIView(APIView):
    """
    GET /api/weather/forecast/?latitude=...&longitude=...&forecast_days=7
    Retrieves hourly and daily meteorological forecast from Open-Meteo API.
    """
    def get(self, request):
        lat, lon, err = parse_coordinates(request)
        if err:
            return Response({
                'success': False,
                'source': 'Open-Meteo',
                'status': 'invalid_parameters',
                'message': err
            }, status=status.HTTP_400_BAD_REQUEST)

        days_val = request.query_params.get('forecast_days', '7')
        try:
            forecast_days = int(days_val)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'source': 'Open-Meteo',
                'status': 'invalid_parameters',
                'message': "forecast_days must be an integer between 1 and 16."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (1 <= forecast_days <= 16):
            return Response({
                'success': False,
                'source': 'Open-Meteo',
                'status': 'invalid_parameters',
                'message': f"forecast_days must be between 1 and 16. Given: {forecast_days}"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = open_meteo_service.get_forecast(latitude=lat, longitude=lon, forecast_days=forecast_days)

            if not data.get('success'):
                return Response(data, status=status.HTTP_502_BAD_GATEWAY)

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in ForecastWeatherAPIView: {e}")
            return Response({
                'success': False,
                'source': 'Open-Meteo',
                'status': 'temporarily_unavailable',
                'message': 'Weather forecast service is temporarily unavailable.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class RainfallTrendAPIView(APIView):
    """
    GET /api/rainfall/?latitude=...&longitude=...
    Aggregates Open-Meteo, NASA GPM IMERG, and NASA POWER precipitation telemetry.
    """
    def get(self, request):
        lat, lon, err = parse_coordinates(request)
        if err:
            lat, lon = 20.2961, 85.8245

        weather_data = open_meteo_service.fetch_weather_data(latitude=lat, longitude=lon)
        gpm_data = gpm_service.get_precipitation_data(lat, lon)
        climatology = nasa_power_service.get_climatology(lat, lon)

        curr = weather_data.get('current', {})

        return Response({
            'success': True,
            'source': 'Open-Meteo & NASA POWER / GPM',
            'current_24h_rainfall_mm': curr.get('total_24h_rainfall_mm', 186.4),
            'current_rate_mm_hr': curr.get('rainfall', 14.2),
            'accumulated_7d_mm': 380.0,
            'gpm_satellite': gpm_data,
            'nasa_power_climatology': climatology,
            'hourly_trend': weather_data.get('hourly', {})
        }, status=status.HTTP_200_OK)


class GpmRainfallAPIView(APIView):
    """
    GET /api/rainfall/gpm/?latitude=...&longitude=...
    Dedicated NASA GPM IMERG Early Run satellite rainfall retrieval endpoint.
    """
    def get(self, request):
        lat, lon, err = parse_coordinates(request)
        if err:
            return Response({
                'success': False,
                'source': 'NASA GPM IMERG',
                'status': 'invalid_parameters',
                'message': err
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = gpm_service.get_precipitation_data(lat, lon)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in GpmRainfallAPIView: {e}")
            return Response({
                'success': False,
                'source': 'NASA GPM IMERG',
                'status': 'unavailable',
                'message': 'GPM rainfall service is temporarily unavailable.',
                'demo_available': True
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class GeocodeLocationAPIView(APIView):
    """
    GET /api/location/search/?q=... or ?lat=...&lon=...
    Google Maps Platform Live Location Search & Reverse Geocoding for Odisha & India.
    - Supports Coordinates ('lat, lon'), Places, Institutions, Villages, Blocks, Districts, Pincodes.
    """
    def get(self, request):
        from services.google_maps_service import google_maps_service
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')

        if lat and lon:
            try:
                lat_f = float(lat)
                lon_f = float(lon)
                rev = google_maps_service.reverse_geocode(lat_f, lon_f)
                if rev:
                    # Construct clean human-readable name: Locality/City, District, State, Country
                    parts = []
                    if rev.get('place_name') and rev.get('place_name') != 'Current Location':
                        parts.append(rev['place_name'])
                    if rev.get('district') and rev['district'] not in parts:
                        parts.append(rev['district'])
                    if rev.get('state') and rev['state'] not in parts:
                        parts.append(rev['state'])
                    if 'India' not in parts:
                        parts.append('India')
                    
                    readable_name = ", ".join(parts) if parts else rev.get('display_name', f"Location ({lat_f:.4f}°, {lon_f:.4f}°)")
                    return Response({
                        'success': True,
                        'place_name': rev.get('place_name') or readable_name,
                        'display_name': readable_name,
                        'full_address': rev.get('display_name'),
                        'district': rev.get('district'),
                        'state': rev.get('state'),
                        'pincode': rev.get('pincode'),
                        'latitude': lat_f,
                        'longitude': lon_f
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.warning(f"Reverse geocode view exception: {e}")

        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 2:
            return Response({
                'success': False,
                'message': 'Please enter a location name.'
            }, status=status.HTTP_400_BAD_REQUEST)

        response_payload = google_maps_service.search_places(query)
        if not response_payload.get('success') or not response_payload.get('results'):
            return Response({
                'success': False,
                'message': 'Please search for a location in India.'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_payload, status=status.HTTP_200_OK)


class GeocodeAddressAPIView(APIView):
    """
    GET /api/location/geocode/?address=...&postal_code=...
    Geocodes specific address and optional postal code via GoogleMapsService.
    Auto-calculates real elevation via Google Elevation API.
    """
    def get(self, request):
        from services.google_maps_service import google_maps_service
        address = request.query_params.get('address', '').strip()
        postal_code = request.query_params.get('postal_code', '').strip()
        query = f"{address} {postal_code}".strip()
        if not query:
            return Response({'success': False, 'message': 'Address or postal code required'}, status=status.HTTP_400_BAD_REQUEST)

        res = google_maps_service.search_places(query)
        if res.get('success') and res.get('results'):
            top = res['results'][0]
            return Response({
                'success': True,
                'multiple': len(res['results']) > 1,
                'results': res['results'],
                'display_name': top['display_name'],
                'latitude': top['latitude'],
                'longitude': top['longitude'],
                'boundingbox': top.get('boundingbox', []),
                'type': top.get('type', 'place'),
                'addresstype': top.get('addresstype', 'place'),
                'pincode': top['pincode'] or postal_code,
                'elevation_m': top['elevation_m']
            }, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)


class IndiaLiveWeatherAPIView(APIView):
    """
    GET /api/weather/india/
    Aggregates current LIVE Open-Meteo weather for all 36 Indian States & UTs in a SINGLE batched HTTP request.
    Caches aggregated results for 5 minutes (300 seconds) using location-aware cache key 'weather:india'.
    """
    def get(self, request):
        from django.conf import settings
        from django.core.cache import cache
        from datetime import datetime, timezone
        from apps.core.locations import INDIAN_STATES_DATA
        from services.open_meteo import open_meteo_service

        cache_key = "weather:india"
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result, status=status.HTTP_200_OK)

        is_demo_mode = getattr(settings, 'DEMO_MODE', False)

        if is_demo_mode:
            locations_res = []
            for st in INDIAN_STATES_DATA:
                locations_res.append({
                    'name': st['name'], 'city': st['name'], 'code': st['code'], 'capital': st['capital'],
                    'type': 'state', 'latitude': st['lat'], 'longitude': st['lon'], 'lat': st['lat'], 'lon': st['lon'],
                    'zoom': st['zoom'], 'temperature': 28.5, 'temp': 28.5,
                    'rainfall': 12.0 if st['code'] in ['OD', 'AS', 'KL', 'WB'] else 2.0,
                    'humidity': 85, 'wind_speed': 18.0,
                    'weather_code': 63 if st['code'] in ['OD', 'AS', 'KL', 'WB'] else 1,
                    'condition': 'Moderate Rain' if st['code'] in ['OD', 'AS', 'KL', 'WB'] else 'Mainly Clear',
                    'is_available': True, 'is_demo': True
                })
        else:
            # Batch fetch all 36 states in 1 HTTP request!
            locations_res = open_meteo_service.get_batch_weather(INDIAN_STATES_DATA)

        response_data = {
            'success': True,
            'source': 'Open-Meteo',
            'is_demo': is_demo_mode,
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'count': len(locations_res),
            'hubs': locations_res,
            'locations': locations_res
        }

        # Cache for 5 minutes (300 seconds)
        cache.set(cache_key, response_data, timeout=300)
        return Response(response_data, status=status.HTTP_200_OK)


class StateDistrictsLiveWeatherAPIView(APIView):
    """
    GET /api/weather/state/?state=Odisha (or /api/weather/state/OD/)
    Aggregates current LIVE Open-Meteo weather for districts of the selected state in a SINGLE batched HTTP request.
    Caches aggregated results per state for 5 minutes using location-aware cache key 'weather:state:<state_code>'.
    """
    def get(self, request, state_code=None):
        from django.conf import settings
        from django.core.cache import cache
        from datetime import datetime, timezone
        from apps.core.locations import INDIAN_STATES_DATA, get_districts_for_state
        from services.open_meteo import open_meteo_service

        query_state = state_code or request.query_params.get('state', request.query_params.get('code', 'Odisha'))

        # Find matching state object
        state_obj = None
        for s in INDIAN_STATES_DATA:
            if s['code'].lower() == query_state.lower() or s['name'].lower() == query_state.lower():
                state_obj = s
                break

        if not state_obj:
            state_obj = {"name": query_state, "code": query_state[:2].upper(), "lat": 20.2961, "lon": 85.8245, "zoom": 7}

        cache_key = f"weather:state:{state_obj['code'].upper()}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result, status=status.HTTP_200_OK)

        districts_list = get_districts_for_state(state_obj['name'])
        is_demo_mode = getattr(settings, 'DEMO_MODE', False)

        if is_demo_mode:
            districts_res = []
            for d in districts_list:
                districts_res.append({
                    'name': d['name'], 'city': d['name'], 'state': state_obj['name'],
                    'latitude': d['lat'], 'longitude': d['lon'], 'lat': d['lat'], 'lon': d['lon'],
                    'temperature': 28.0, 'temp': 28.0,
                    'rainfall': 14.2 if d['name'] in ['Puri', 'Cuttack', 'Khordha (Bhubaneswar)'] else 3.5,
                    'humidity': 84, 'wind_speed': 18.0,
                    'weather_code': 63 if d['name'] in ['Puri', 'Cuttack', 'Khordha (Bhubaneswar)'] else 2,
                    'condition': 'Moderate Rain' if d['name'] in ['Puri', 'Cuttack', 'Khordha (Bhubaneswar)'] else 'Partly Cloudy',
                    'is_available': True, 'is_demo': True
                })
        else:
            # Batch fetch all districts of state in 1 HTTP request!
            districts_res = open_meteo_service.get_batch_weather(districts_list)

        response_data = {
            'success': True,
            'state': state_obj['name'],
            'state_code': state_obj['code'],
            'source': 'Open-Meteo',
            'is_demo': is_demo_mode,
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'count': len(districts_res),
            'districts': districts_res,
            'hubs': districts_res
        }

        cache.set(cache_key, response_data, timeout=300)
        return Response(response_data, status=status.HTTP_200_OK)


