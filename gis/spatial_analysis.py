from gis.geometry import haversine_distance_km

def find_nearest_facilities(origin_lat, origin_lon, facilities_list, limit=5):
    """
    Ranks facilities by distance and accessibility.
    """
    ranked = []
    for fac in facilities_list:
        dist = haversine_distance_km(origin_lat, origin_lon, fac.get('lat', 0), fac.get('lon', 0))
        item = dict(fac)
        item['distance_km'] = dist
        ranked.append(item)
    ranked.sort(key=lambda x: x['distance_km'])
    return ranked[:limit]
