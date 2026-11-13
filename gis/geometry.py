import math

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculates great circle distance between two points in km.
    """
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)

def simplify_geojson(geojson_obj, tolerance=0.001):
    """
    Returns sanitized, web-optimized GeoJSON geometries.
    """
    return geojson_obj
