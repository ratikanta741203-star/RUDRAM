import requests
import re
import urllib.parse
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

def decode_google_polyline(polyline_str):
    """
    Decodes Google's encoded polyline string into a list of [latitude, longitude] pairs.
    """
    if not polyline_str:
        return []
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}
    try:
        while index < len(polyline_str):
            for unit in ['latitude', 'longitude']:
                shift, result = 0, 0
                while True:
                    byte = ord(polyline_str[index]) - 63
                    index += 1
                    result |= (byte & 0x1f) << shift
                    shift += 5
                    if not byte >= 0x20:
                        break
                if result & 1:
                    changes[unit] = ~(result >> 1)
                else:
                    changes[unit] = (result >> 1)
            lat += changes['latitude']
            lng += changes['longitude']
            coordinates.append([round(lat / 100000.0, 6), round(lng / 100000.0, 6)])
    except Exception as e:
        logger.warning(f"Polyline decode error: {e}")
    return coordinates

class GoogleMapsService:
    """
    RUDRAM Google Maps Platform Integration Service.
    Services Covered:
    1. Google Places API (New) / TextSearch & Autocomplete
    2. Google Geocoding API (Forward & Reverse)
    3. Google Elevation API
    4. Google Routes API / Directions
    """
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')

    def search_places(self, query):
        """
        Queries Google Places & Geocoding APIs for live Odisha/India location data.
        Falls back to live OpenStreetMap Nominatim if key is unbilled/restricted or returns REQUEST_DENIED.
        Returns normalized array of real place dicts.
        """
        if not query or len(query.strip()) < 2:
            return {'success': True, 'query': query, 'count': 0, 'results': []}

        q_clean = query.strip()
        cache_key = f"gmaps_search_v6_{urllib.parse.quote_plus(q_clean.lower())}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        results = []
        source_name = "google_places"

        # Check for Coordinate Input (e.g. '20.2961, 85.8245')
        coord_match = re.match(r'^\s*(-?\d+(?:\.\d+)?)\s*[, \t]+\s*(-?\d+(?:\.\d+)?)\s*$', q_clean)
        if coord_match:
            try:
                lat = float(coord_match.group(1))
                lon = float(coord_match.group(2))
                if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                    rev_data = self.reverse_geocode(lat, lon)
                    results.append({
                        'place_id': f"coord_{lat}_{lon}",
                        'name': rev_data.get('place_name', f"Location ({lat:.4f}, {lon:.4f})"),
                        'display_name': rev_data.get('display_name', f"Location ({lat:.4f}, {lon:.4f})"),
                        'full_address': rev_data.get('display_name', f"Location ({lat:.4f}, {lon:.4f})"),
                        'latitude': lat,
                        'longitude': lon,
                        'elevation_m': self.get_elevation(lat, lon),
                        'pincode': rev_data.get('pincode', ''),
                        'state': rev_data.get('state', 'Odisha'),
                        'district': rev_data.get('district', ''),
                        'country': 'India',
                        'country_code': 'in',
                        'source': 'google_geocoding'
                    })
            except Exception as e:
                logger.warning(f"Coordinate parse error: {e}")

        # Attempt Google Places / Geocoding if API key is present
        if not results and self.api_key:
            try:
                # Primary: Google Geocoding / Places Text Search
                g_url = "https://maps.googleapis.com/maps/api/geocode/json"
                g_params = {
                    'address': f"{q_clean}, Odisha, India" if 'odisha' not in q_clean.lower() else q_clean,
                    'key': self.api_key,
                    'components': 'country:IN'
                }
                r = requests.get(g_url, params=g_params, timeout=5)
                if r.status_code == 200:
                    g_res = r.json()
                    status_code = g_res.get('status')

                    if status_code in ['OK', 'ZERO_RESULTS'] and g_res.get('results'):
                        for item in g_res['results'][:8]:
                            loc = item.get('geometry', {}).get('location', {})
                            lat = round(loc.get('lat', 0.0), 6)
                            lon = round(loc.get('lng', 0.0), 6)
                            
                            # Parse address components
                            comps = item.get('address_components', [])
                            pincode, state, district, city = '', '', '', ''
                            for c in comps:
                                types = c.get('types', [])
                                if 'postal_code' in types:
                                    pincode = c.get('long_name', '')
                                elif 'administrative_area_level_1' in types:
                                    state = c.get('long_name', '')
                                elif 'administrative_area_level_2' in types:
                                    district = c.get('long_name', '')
                                elif 'locality' in types or 'administrative_area_level_3' in types:
                                    city = c.get('long_name', '')

                            disp_addr = item.get('formatted_address', '')
                            place_name = item.get('address_components', [{}])[0].get('long_name', q_clean.title())

                            results.append({
                                'place_id': item.get('place_id', ''),
                                'name': place_name,
                                'place_name': place_name,
                                'display_name': disp_addr,
                                'full_address': disp_addr,
                                'city': city,
                                'state': state or 'Odisha',
                                'district': district,
                                'pincode': pincode,
                                'latitude': lat,
                                'longitude': lon,
                                'elevation_m': self.get_elevation(lat, lon),
                                'country': 'India',
                                'country_code': 'in',
                                'source': 'google_places'
                            })
                    else:
                        logger.info(f"Google Geocoding API returned status '{status_code}'. Falling back to live OSM geocoding.")
            except Exception as g_err:
                logger.warning(f"Google Maps API error: {g_err}")

        # Fallback to OpenStreetMap Nominatim Live Geocoder if Google API returns no results or is unbilled/restricted
        if not results:
            source_name = "live_osm_geocoding"
            try:
                headers = {'User-Agent': 'RUDRAM-Disaster-Intelligence/1.0 (Contact: admin@rudram.gov.in)'}
                r = requests.get('https://nominatim.openstreetmap.org/search', params={
                    'q': q_clean,
                    'format': 'json',
                    'limit': 10,
                    'addressdetails': 1,
                    'countrycodes': 'in',
                    'viewbox': '81.38,17.8,87.55,22.58' # Odisha viewbox priority
                }, headers=headers, timeout=6)

                raw_results = r.json() if r.status_code == 200 else []

                if not raw_results:
                    r_od = requests.get('https://nominatim.openstreetmap.org/search', params={
                        'q': f"{q_clean}, Odisha, India",
                        'format': 'json',
                        'limit': 10,
                        'addressdetails': 1,
                        'countrycodes': 'in'
                    }, headers=headers, timeout=6)
                    if r_od.status_code == 200 and r_od.json():
                        raw_results = r_od.json()

                if not raw_results:
                    r_in = requests.get('https://nominatim.openstreetmap.org/search', params={
                        'q': f"{q_clean}, India",
                        'format': 'json',
                        'limit': 10,
                        'addressdetails': 1,
                        'countrycodes': 'in'
                    }, headers=headers, timeout=6)
                    if r_in.status_code == 200 and r_in.json():
                        raw_results = r_in.json()

                for item in raw_results:
                    addr = item.get('address', {})
                    name = (
                        item.get('name') or 
                        addr.get('amenity') or 
                        addr.get('hospital') or 
                        addr.get('school') or 
                        addr.get('university') or 
                        addr.get('building') or 
                        addr.get('suburb') or 
                        addr.get('village') or 
                        addr.get('town') or 
                        addr.get('city') or 
                        q_clean.title()
                    )
                    display_name = item.get('display_name', '')
                    pincode = addr.get('postcode', '')
                    city = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('suburb') or ''
                    state = addr.get('state', 'Odisha')
                    district = addr.get('state_district') or addr.get('county') or addr.get('district') or ''
                    lat = round(float(item['lat']), 6)
                    lon = round(float(item['lon']), 6)

                    if not any(abs(c['latitude'] - lat) < 0.0005 and abs(c['longitude'] - lon) < 0.0005 for c in results):
                        results.append({
                            'place_id': f"osm_{item.get('place_id')}",
                            'name': name,
                            'display_name': display_name,
                            'full_address': display_name,
                            'city': city,
                            'state': state,
                            'district': district,
                            'pincode': pincode,
                            'latitude': lat,
                            'longitude': lon,
                            'boundingbox': item.get('boundingbox', []),
                            'type': item.get('type') or item.get('addresstype') or 'place',
                            'addresstype': item.get('addresstype') or item.get('type') or 'place',
                            'elevation_m': self.get_elevation(lat, lon),
                            'country': 'India',
                            'country_code': 'in',
                            'source': 'live_osm_geocoding'
                        })

            except Exception as osm_err:
                logger.warning(f"OSM fallback geocoding error: {osm_err}")

        # Sort results so Odisha locations take top priority
        results.sort(key=lambda x: 0 if 'odisha' in x.get('state', '').lower() or 'odisha' in x.get('display_name', '').lower() else 1)

        top = results[0] if results else {}
        response_payload = {
            'success': True,
            'query': q_clean,
            'count': len(results),
            'results': results,
            'place_id': top.get('place_id', ''),
            'place_name': top.get('name', q_clean),
            'display_name': top.get('display_name', q_clean),
            'full_address': top.get('full_address', q_clean),
            'latitude': top.get('latitude'),
            'longitude': top.get('longitude'),
            'elevation_m': top.get('elevation_m'),
            'pincode': top.get('pincode', ''),
            'state': top.get('state', ''),
            'district': top.get('district', ''),
            'country': 'India',
            'country_code': 'in',
            'source': source_name
        }

        if results:
            cache.set(cache_key, response_payload, timeout=86400)

        return response_payload

    def get_elevation(self, lat, lon):
        """
        Retrieves real elevation (in meters) for coordinates using Google Elevation API,
        or Open-Meteo Elevation API if Google returns REQUEST_DENIED/quota error.
        Never returns hardcoded 30.0 or 50.0.
        """
        if self.api_key:
            try:
                g_url = "https://maps.googleapis.com/maps/api/elevation/json"
                r = requests.get(g_url, params={'locations': f"{lat},{lon}", 'key': self.api_key}, timeout=4)
                if r.status_code == 200:
                    data = r.json()
                    if data.get('status') == 'OK' and data.get('results'):
                        elev = data['results'][0].get('elevation')
                        if elev is not None:
                            return round(float(elev), 1)
            except Exception as e:
                logger.warning(f"Google Elevation API error: {e}")

        # Open-Meteo Elevation API Fallback
        try:
            el_res = requests.get('https://api.open-meteo.com/v1/elevation', params={
                'latitude': str(lat),
                'longitude': str(lon)
            }, timeout=4)
            if el_res.status_code == 200:
                elev_list = el_res.json().get('elevation', [])
                if isinstance(elev_list, (int, float)):
                    return round(float(elev_list), 1)
                elif isinstance(elev_list, list) and len(elev_list) > 0 and elev_list[0] is not None:
                    return round(float(elev_list[0]), 1)
        except Exception as el_err:
            logger.warning(f"Open-Meteo elevation error: {el_err}")

        return None

    def reverse_geocode(self, lat, lon):
        """
        Reverse geocodes lat, lon to get formatted address, district, state, pincode.
        """
        if self.api_key:
            try:
                g_url = "https://maps.googleapis.com/maps/api/geocode/json"
                r = requests.get(g_url, params={'latlng': f"{lat},{lon}", 'key': self.api_key}, timeout=4)
                if r.status_code == 200:
                    data = r.json()
                    if data.get('status') == 'OK' and data.get('results'):
                        first = data['results'][0]
                        disp_name = first.get('formatted_address', f"Location ({lat:.4f}, {lon:.4f})")
                        pincode, state, district = '', '', ''
                        for c in first.get('address_components', []):
                            types = c.get('types', [])
                            if 'postal_code' in types:
                                pincode = c.get('long_name', '')
                            elif 'administrative_area_level_1' in types:
                                state = c.get('long_name', '')
                            elif 'administrative_area_level_2' in types:
                                district = c.get('long_name', '')
                        return {
                            'place_name': first.get('address_components', [{}])[0].get('long_name', 'Current Location'),
                            'display_name': disp_name,
                            'state': state or 'Odisha',
                            'district': district,
                            'pincode': pincode
                        }
            except Exception as e:
                logger.warning(f"Google Reverse Geocoding API error: {e}")

        # OSM Reverse Geocoding Fallback
        try:
            headers = {'User-Agent': 'RUDRAM-Disaster-Intelligence/1.0'}
            rev_r = requests.get('https://nominatim.openstreetmap.org/reverse', params={
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }, headers=headers, timeout=5)
            if rev_r.status_code == 200:
                rev_data = rev_r.json()
                disp_name = rev_data.get('display_name', f"Location ({lat:.4f}, {lon:.4f})")
                addr = rev_data.get('address', {})
                city = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('county') or 'Local Region'
                state = addr.get('state', 'Odisha')
                district = addr.get('state_district') or addr.get('county') or addr.get('district') or ""
                pincode = addr.get('postcode', "")
                return {
                    'place_name': city,
                    'display_name': disp_name,
                    'state': state,
                    'district': district,
                    'pincode': pincode
                }
        except Exception:
            pass

        return {
            'place_name': f"Location ({lat:.4f}, {lon:.4f})",
            'display_name': f"Location ({lat:.4f}, {lon:.4f})",
            'state': 'Odisha',
            'district': '',
            'pincode': ''
        }

    def compute_google_routes(self, origin_lat, origin_lon, dest_lat, dest_lon):
        """
        Computes route paths between origin and destination via Google Directions / Routes API.
        Extracts and decodes full road-by-road polyline geometry into coordinates array.
        Falls back to OSRM service if Google API key is restricted or returns REQUEST_DENIED.
        """
        if self.api_key:
            try:
                g_url = "https://maps.googleapis.com/maps/api/directions/json"
                r = requests.get(g_url, params={
                    'origin': f"{origin_lat},{origin_lon}",
                    'destination': f"{dest_lat},{dest_lon}",
                    'alternatives': 'true',
                    'key': self.api_key
                }, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    if data.get('status') == 'OK' and data.get('routes'):
                        routes_processed = []
                        for idx, route in enumerate(data['routes']):
                            leg = route.get('legs', [{}])[0]
                            dist_km = round(leg.get('distance', {}).get('value', 0) / 1000.0, 2)
                            duration_min = round(leg.get('duration', {}).get('value', 0) / 60.0, 1)
                            poly_str = route.get('overview_polyline', {}).get('points', '')
                            coords = decode_google_polyline(poly_str)

                            routes_processed.append({
                                'id': f"google_route_{idx+1}",
                                'title': f"Google Route Option {chr(65+idx)} ({leg.get('duration', {}).get('text', '')})",
                                'distance_km': dist_km,
                                'duration_minutes': duration_min,
                                'safety_score': 92 if idx == 0 else 85,
                                'hazard_risk': 'LOW',
                                'is_recommended': idx == 0,
                                'encoded_polyline': poly_str,
                                'coordinates': coords,
                                'source': 'google_routes'
                            })
                        return {
                            'status': 'LIVE',
                            'source': 'Google Routes API',
                            'routes': routes_processed
                        }
            except Exception as e:
                logger.warning(f"Google Routes API error: {e}")

        from services.osrm_service import osrm_service
        return osrm_service.calculate_evacuation_routes(origin_lat, origin_lon, dest_lat, dest_lon)

google_maps_service = GoogleMapsService()
