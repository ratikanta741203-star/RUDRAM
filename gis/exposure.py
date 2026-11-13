from gis.geometry import haversine_distance_km

def calculate_population_exposure(total_pop, density, flood_extent_sqkm, avg_elevation):
    """
    Computes exposure metrics based on spatial flood overlay.
    """
    exposed = min(total_pop, int(flood_extent_sqkm * density * 0.65))
    vulnerable = int(exposed * 0.28) # elderly, children, disabled
    critical = int(exposed * 0.18) # immediate riverbank / zero-elevation
    shelter_deficit = max(0, exposed - 12000)

    exposure_score = min(100, int((exposed / max(1, total_pop)) * 100 * 1.5 + (density / 5000) * 20))

    return {
        'total_population': total_pop,
        'exposed_population': exposed,
        'vulnerable_population': vulnerable,
        'critical_population': critical,
        'shelter_deficit': shelter_deficit,
        'exposure_score': exposure_score
    }
