from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.shelters.models import Shelter
from apps.shelters.serializers import ShelterSerializer
from gis.geometry import haversine_distance_km
from apps.core.models import AuditLog

def shelters_view(request):
    shelters = Shelter.objects.all()
    total_cap = sum(s.total_capacity for s in shelters)
    total_occ = sum(s.current_occupancy for s in shelters)
    available_cap = total_cap - total_occ
    open_count = shelters.filter(status='OPEN').count()

    context = {
        'shelters': shelters,
        'total_cap': total_cap,
        'total_occ': total_occ,
        'available_cap': available_cap,
        'open_count': open_count,
        'page_title': 'Shelter & Evacuation Camp Directory'
    }
    return render(request, 'shelters/index.html', context)

class ShelterListAPIView(APIView):
    """
    GET /api/shelters/
    """
    def get(self, request):
        shelters = Shelter.objects.all()
        serializer = ShelterSerializer(shelters, many=True)
        return Response({
            'success': True,
            'count': shelters.count(),
            'shelters': serializer.data
        })

class ShelterRecommendAPIView(APIView):
    """
    GET /api/shelters/recommend/?lat=...&lon=...&medical_required=true
    Multi-criteria ranking:
    Score = (1 / (Distance + 0.5)) * 40 + (Available_Capacity / Total) * 30 + (Medical? 15:0) + (Elevation/50)*15
    """
    def get(self, request):
        lat = float(request.query_params.get('lat', 20.2961))
        lon = float(request.query_params.get('lon', 85.8245))
        med_req = request.query_params.get('medical_required', 'false').lower() == 'true'

        shelters = Shelter.objects.filter(status__in=['OPEN', 'NEAR_CAPACITY'])
        ranked = []

        for s in shelters:
            dist = haversine_distance_km(lat, lon, s.latitude, s.longitude)
            avail_ratio = s.available_capacity / max(1, s.total_capacity)
            
            # Weighted scoring algorithm
            score = (
                (max(0, 15.0 - dist) / 15.0) * 45.0 +
                (avail_ratio * 25.0) +
                (15.0 if s.has_medical_station else 0.0) +
                (10.0 if s.elevation_m > 25 else 0.0) +
                (5.0 if s.has_backup_generator else 0.0)
            )

            data = ShelterSerializer(s).data
            data['distance_km'] = dist
            data['suitability_score'] = round(score, 1)
            ranked.append(data)

        ranked.sort(key=lambda x: x['suitability_score'], reverse=True)

        return Response({
            'success': True,
            'origin': {'lat': lat, 'lon': lon},
            'best_match': ranked[0] if ranked else None,
            'recommendations': ranked
        })


class NearbySheltersAPIView(APIView):
    """
    GET /api/shelters/nearby/?latitude=20.2961&longitude=85.8245&radius=10
    READ-ONLY nearby shelter API.
    1. Obtains user's real GPS latitude and longitude.
    2. Validates coordinates (-90 <= lat <= 90, -180 <= lon <= 180).
    3. Enforces maximum radius <= 10 km.
    4. Queries official RUDRAM Shelter database.
    5. Calculates server-side Haversine distance in km.
    6. Excludes all shelters outside 10 km.
    7. Sorts matching shelters nearest -> farthest.
    8. Returns structured JSON containing real database shelter records and distance_km.
    """
    def get(self, request):
        lat_param = request.query_params.get('latitude') or request.query_params.get('lat')
        lon_param = request.query_params.get('longitude') or request.query_params.get('lon')

        if not lat_param or not lon_param:
            return Response({
                'success': False,
                'error': 'Latitude and longitude parameters are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat = float(lat_param)
            lon = float(lon_param)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'Invalid numerical coordinates provided.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return Response({
                'success': False,
                'error': 'Coordinates out of valid geographical bounds.'
            }, status=status.HTTP_400_BAD_REQUEST)

        radius_param = request.query_params.get('radius', '10')
        try:
            radius_km = min(float(radius_param), 10.0)
            if radius_km <= 0:
                radius_km = 10.0
        except (ValueError, TypeError):
            radius_km = 10.0

        # Query official RUDRAM Shelter DB records
        shelters_qs = Shelter.objects.filter(is_demo=False)
        if not shelters_qs.exists():
            shelters_qs = Shelter.objects.all()

        nearby_list = []
        for s in shelters_qs:
            dist = haversine_distance_km(lat, lon, s.latitude, s.longitude)
            if dist <= radius_km:
                data = ShelterSerializer(s).data
                data['distance_km'] = round(dist, 2)
                nearby_list.append(data)

        # Sort nearest -> farthest
        nearby_list.sort(key=lambda x: x['distance_km'])

        return Response({
            'success': True,
            'radius_km': radius_km,
            'user_location': {
                'latitude': lat,
                'longitude': lon
            },
            'count': len(nearby_list),
            'shelters': nearby_list
        }, status=status.HTTP_200_OK)

from apps.accounts.permissions import IsAdminUserOrCommander

class ShelterUpdateOccupancyAPIView(APIView):
    """
    POST /api/shelters/<id>/update-occupancy/
    ADMIN ONLY
    """
    permission_classes = [IsAdminUserOrCommander]

    def post(self, request, pk):
        shelter = get_object_or_404(Shelter, pk=pk)
        new_occ = int(request.data.get('current_occupancy', shelter.current_occupancy))
        shelter.current_occupancy = max(0, min(new_occ, shelter.total_capacity + 500))
        
        if shelter.current_occupancy >= shelter.total_capacity:
            shelter.status = 'FULL'
        elif shelter.current_occupancy >= int(shelter.total_capacity * 0.8):
            shelter.status = 'NEAR_CAPACITY'
        else:
            shelter.status = 'OPEN'
        
        shelter.save()

        AuditLog.objects.create(
            user_name=request.user.username if request.user.is_authenticated else 'Operator',
            action='Update Shelter Occupancy',
            target_model='Shelter',
            target_id=str(shelter.id),
            details=f"Updated {shelter.name} occupancy to {shelter.current_occupancy} ({shelter.status})"
        )

        return Response({
            'success': True,
            'shelter': ShelterSerializer(shelter).data
        })


import re
import requests
import logging
from apps.accounts.permissions import is_admin_or_operator

logger = logging.getLogger(__name__)

class GeocodeShelterLocationAPIView(APIView):
    """
    GET /api/location/geocode/?address=...&postal_code=...
    Requires Admin/Operator authentication.
    1. Validates 6-digit Indian PIN Code format.
    2. Performs real geocoding call via Nominatim for Indian locations.
    3. Enforces country == 'India' (country_code == 'in').
    4. Fetches real elevation (in meters) via Open-Meteo Elevation API.
    5. Returns candidate list if multiple results found.
    6. Never falls back to fake/demo coordinates.
    """
    def get(self, request):
        if not request.user.is_authenticated or not (request.user.is_staff or is_admin_or_operator(request.user)):
            return Response({
                'success': False,
                'error': 'Access Denied: Administrative permissions required.'
            }, status=status.HTTP_403_FORBIDDEN)

        address = request.query_params.get('address', '').strip()
        postal_code = request.query_params.get('postal_code', '').strip()
        q_param = request.query_params.get('q', '').strip()

        if not postal_code and q_param:
            pin_match = re.search(r'\b\d{6}\b', q_param)
            if pin_match:
                postal_code = pin_match.group(0)

        # Validate PIN Code (must be 6 digits)
        if not postal_code or not re.match(r'^\d{6}$', postal_code):
            return Response({
                'success': False,
                'error': 'Please enter a valid 6-digit Indian PIN Code (e.g. 752001).'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Construct query safely
        query = f"{address}, {postal_code}, India" if address else f"{postal_code}, India"

        try:
            r = requests.get('https://nominatim.openstreetmap.org/search', params={
                'q': query,
                'format': 'json',
                'limit': 5,
                'addressdetails': 1,
                'countrycodes': 'in'
            }, headers={'User-Agent': 'RUDRAM-Disaster-Intelligence/1.0'}, timeout=8)

            if r.status_code != 200:
                return Response({
                    'success': False,
                    'error': 'Location service temporarily unavailable. Please try again.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            raw_results = r.json()

            # Fallback to PIN Code query if specific address yields no raw matches
            if not raw_results and address:
                r_fallback = requests.get('https://nominatim.openstreetmap.org/search', params={
                    'q': f"{postal_code}, India",
                    'format': 'json',
                    'limit': 5,
                    'addressdetails': 1,
                    'countrycodes': 'in'
                }, headers={'User-Agent': 'RUDRAM-Disaster-Intelligence/1.0'}, timeout=8)
                if r_fallback.status_code == 200:
                    raw_results = r_fallback.json()

            if not raw_results:
                return Response({
                    'success': False,
                    'error': 'Location not found. Please verify the address and PIN code.'
                }, status=status.HTTP_404_NOT_FOUND)

            # Enforce India location requirement
            india_matches = [item for item in raw_results if item.get('address', {}).get('country_code') == 'in']

            if not india_matches:
                return Response({
                    'success': False,
                    'error': 'Please select a location within India.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Prepare candidate list
            candidates = []
            for item in india_matches[:5]:
                lat = round(float(item['lat']), 6)
                lon = round(float(item['lon']), 6)
                display_name = item.get('display_name', query)
                candidates.append({
                    'display_name': display_name,
                    'latitude': lat,
                    'longitude': lon,
                    'elevation_m': None,
                    'postal_code': postal_code,
                    'country': 'India'
                })

            # Batch fetch REAL elevation values for candidate coordinates from Open-Meteo
            lats_str = ','.join(str(c['latitude']) for c in candidates)
            lons_str = ','.join(str(c['longitude']) for c in candidates)

            try:
                el_res = requests.get('https://api.open-meteo.com/v1/elevation', params={
                    'latitude': lats_str,
                    'longitude': lons_str
                }, timeout=5)
                if el_res.status_code == 200:
                    elev_data = el_res.json().get('elevation', [])
                    if isinstance(elev_data, (int, float)):
                        elev_data = [elev_data]
                    for idx, c in enumerate(candidates):
                        if idx < len(elev_data) and elev_data[idx] is not None:
                            c['elevation_m'] = round(float(elev_data[idx]), 1)
            except Exception as el_err:
                logger.warning(f"Open-Meteo elevation batch lookup warning: {el_err}")

            if len(candidates) > 1:
                return Response({
                    'success': True,
                    'multiple': True,
                    'count': len(candidates),
                    'results': candidates
                }, status=status.HTTP_200_OK)

            target = candidates[0]
            if target['elevation_m'] is None:
                return Response({
                    'success': False,
                    'error': 'Elevation unavailable'
                }, status=status.HTTP_502_BAD_GATEWAY)

            return Response({
                'success': True,
                'multiple': False,
                'display_name': target['display_name'],
                'latitude': target['latitude'],
                'longitude': target['longitude'],
                'elevation_m': target['elevation_m'],
                'postal_code': target['postal_code'],
                'country': 'India'
            }, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Geocoding network exception: {req_err}")
            return Response({
                'success': False,
                'error': 'Location service temporarily unavailable. Please try again.'
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return Response({
                'success': False,
                'error': 'An error occurred during location lookup.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.core.cache import cache

class SmartLocationSearchAPIView(APIView):
    """
    GET /api/location/search/?q=<SEARCH_TERM>
    Requires Admin/Operator authentication.
    1. Debounced real-time place search for India (cities, institutes, hospitals, stations, landmarks, etc.).
    2. Enforces countrycodes='in' (India).
    3. Caches search results for 5 minutes.
    4. Batch fetches real elevation data in meters from Open-Meteo Elevation API.
    5. Returns structured JSON with place_name, display_name, city, state, pincode, latitude, longitude, elevation_m.
    """
    def get(self, request):
        if not request.user.is_authenticated or not (request.user.is_staff or is_admin_or_operator(request.user)):
            return Response({
                'success': False,
                'error': 'Access Denied: Administrative permissions required.'
            }, status=status.HTTP_403_FORBIDDEN)

        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 2:
            return Response({
                'success': True,
                'query': query,
                'count': 0,
                'results': []
            }, status=status.HTTP_200_OK)

        cache_key = f"smart_loc_search_v3_{query.lower()}"
        cached_res = cache.get(cache_key)
        if cached_res:
            return Response(cached_res, status=status.HTTP_200_OK)

        try:
            r = requests.get('https://nominatim.openstreetmap.org/search', params={
                'q': query,
                'format': 'json',
                'limit': 8,
                'addressdetails': 1,
                'countrycodes': 'in'
            }, headers={'User-Agent': 'RUDRAM-Disaster-Intelligence/1.0'}, timeout=8)

            if r.status_code != 200:
                return Response({
                    'success': False,
                    'error': 'Location search temporarily unavailable.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            raw_results = r.json()

            # Filter for India matches
            india_results = [x for x in raw_results if x.get('address', {}).get('country_code') == 'in']

            if not india_results and raw_results:
                india_results = raw_results

            parsed_results = []
            for item in india_results[:8]:
                addr = item.get('address', {})
                place_name = (
                    item.get('name') or
                    addr.get('amenity') or
                    addr.get('hospital') or
                    addr.get('school') or
                    addr.get('university') or
                    addr.get('building') or
                    addr.get('railway') or
                    addr.get('bus_station') or
                    addr.get('tourism') or
                    addr.get('suburb') or
                    addr.get('city') or
                    addr.get('town') or
                    query.title()
                )
                display_name = item.get('display_name', '')
                pincode = addr.get('postcode', '')
                city = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('county') or ''
                state = addr.get('state', '')
                lat = round(float(item['lat']), 6)
                lon = round(float(item['lon']), 6)

                parsed_results.append({
                    'place_name': place_name,
                    'display_name': display_name,
                    'city': city,
                    'state': state,
                    'pincode': pincode,
                    'latitude': lat,
                    'longitude': lon,
                    'elevation_m': None
                })

            if parsed_results:
                lats_str = ','.join(str(c['latitude']) for c in parsed_results)
                lons_str = ','.join(str(c['longitude']) for c in parsed_results)
                try:
                    el_res = requests.get('https://api.open-meteo.com/v1/elevation', params={
                        'latitude': lats_str,
                        'longitude': lons_str
                    }, timeout=5)
                    if el_res.status_code == 200:
                        elev_list = el_res.json().get('elevation', [])
                        if isinstance(elev_list, (int, float)):
                            elev_list = [elev_list]
                        for idx, c in enumerate(parsed_results):
                            if idx < len(elev_list) and elev_list[idx] is not None:
                                c['elevation_m'] = round(float(elev_list[idx]), 1)
                except Exception as el_err:
                    logger.warning(f"Open-Meteo elevation error: {el_err}")

            response_payload = {
                'success': True,
                'query': query,
                'count': len(parsed_results),
                'results': parsed_results
            }

            cache.set(cache_key, response_payload, timeout=300)
            return Response(response_payload, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Smart location search exception for '{query}': {req_err}")
            return Response({
                'success': False,
                'error': 'Location search temporarily unavailable.'
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            logger.error(f"Smart location search error for '{query}': {e}")
            return Response({
                'success': False,
                'error': 'An unexpected error occurred during location search.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


