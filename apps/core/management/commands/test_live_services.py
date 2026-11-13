from django.core.management.base import BaseCommand
from django.conf import settings
import logging

class Command(BaseCommand):
    help = "Audits and tests all external data service adapters, remote sensing feeds, and ML model connections."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("======================================================================"))
        self.stdout.write(self.style.NOTICE("RUDRAM - EXTERNAL LIVE DATA SERVICES & TELEMETRY AUDIT"))
        self.stdout.write(self.style.NOTICE("======================================================================"))
        self.stdout.write(f"DEMO_MODE: {getattr(settings, 'DEMO_MODE', False)}")
        self.stdout.write(f"MODEL_PATH: {getattr(settings, 'MODEL_PATH', '')}")
        self.stdout.write("----------------------------------------------------------------------")
        self.stdout.write(f"{'SERVICE':<28} {'STATUS':<18} {'LATENCY / DETAILS'}")
        self.stdout.write("----------------------------------------------------------------------")

        # 1. Open-Meteo Live Weather
        try:
            from services.open_meteo import open_meteo_service
            weather = open_meteo_service.get_current_weather(20.2961, 85.8245)
            if weather and weather.get('success') and not weather.get('is_demo'):
                curr = weather.get('current', {})
                self.stdout.write(f"{'Open-Meteo Weather':<28} {self.style.SUCCESS('LIVE'):<18} {curr.get('temperature')}°C | {curr.get('condition')}")
            else:
                self.stdout.write(f"{'Open-Meteo Weather':<28} {self.style.WARNING('UNAVAILABLE'):<18} Upstream Offline / Rate Limited")
        except Exception as e:
            self.stdout.write(f"{'Open-Meteo Weather':<28} {self.style.ERROR('ERROR'):<18} {type(e).__name__}")

        # 2. NASA POWER Climatology
        try:
            from services.nasa_power_service import nasa_power_service
            power = nasa_power_service.get_climatology(20.2961, 85.8245)
            if power and power.get('status') == 'LIVE':
                self.stdout.write(f"{'NASA POWER Climatology':<28} {self.style.SUCCESS('LIVE'):<18} Connected ({power.get('source')})")
            elif power and power.get('is_demo'):
                self.stdout.write(f"{'NASA POWER Climatology':<28} {self.style.WARNING('DEMO_MODE'):<18} Simulated Climatology Active")
            else:
                self.stdout.write(f"{'NASA POWER Climatology':<28} {self.style.NOTICE('UNAVAILABLE'):<18} Upstream Server Busy")
        except Exception as e:
            self.stdout.write(f"{'NASA POWER Climatology':<28} {self.style.ERROR('ERROR'):<18} {type(e).__name__}")

        # 3. NASA GPM IMERG
        try:
            from services.gpm_service import gpm_service
            gpm_res = gpm_service.get_precipitation_data(20.2961, 85.8245)
            if gpm_res and gpm_res.get('status') == 'LIVE':
                self.stdout.write(f"{'NASA GPM IMERG Rainfall':<28} {self.style.SUCCESS('LIVE'):<18} {gpm_res.get('satellite_rain_rate_mm_hr')} mm/h")
            elif gpm_res and gpm_res.get('is_demo'):
                self.stdout.write(f"{'NASA GPM IMERG Rainfall':<28} {self.style.WARNING('DEMO_MODE'):<18} Simulated Precipitation Active")
            else:
                self.stdout.write(f"{'NASA GPM IMERG Rainfall':<28} {self.style.NOTICE('UNAVAILABLE'):<18} Earthdata Auth / CMR Reachable")
        except Exception as e:
            self.stdout.write(f"{'NASA GPM IMERG Rainfall':<28} {self.style.ERROR('ERROR'):<18} {type(e).__name__}")

        # 4. Google Earth Engine
        try:
            from services.gee_service import gee_service
            gee_stat = gee_service.get_connection_status()
            if gee_stat.get('authenticated'):
                self.stdout.write(f"{'Google Earth Engine':<28} {self.style.SUCCESS('LIVE'):<18} Copernicus Sentinel-1/2 Authenticated")
            elif gee_stat.get('credential_file_found'):
                self.stdout.write(f"{'Google Earth Engine':<28} {self.style.WARNING('UNAVAILABLE'):<18} Service Account Key Found / EE Init Failed")
            else:
                self.stdout.write(f"{'Google Earth Engine':<28} {self.style.NOTICE('NOT_CONFIGURED'):<18} Credential File Awaited")
        except Exception as e:
            self.stdout.write(f"{'Google Earth Engine':<28} {self.style.ERROR('ERROR'):<18} {type(e).__name__}")

        # 5. NASA FIRMS
        try:
            from services.firms_service import firms_service
            firms_res = firms_service.get_fire_hotspots(20.2961, 85.8245, 0.5)
            if firms_res and firms_res.get('status') == 'LIVE':
                self.stdout.write(f"{'NASA FIRMS Thermal':<28} {self.style.SUCCESS('LIVE'):<18} {len(firms_res.get('hotspots', []))} Active Hotspots")
            elif firms_res and firms_res.get('status') == 'CONFIGURATION_REQUIRED':
                self.stdout.write(f"{'NASA FIRMS Thermal':<28} {self.style.NOTICE('NOT_CONFIGURED'):<18} Missing FIRMS_API_KEY")
            elif firms_res and firms_res.get('is_demo'):
                self.stdout.write(f"{'NASA FIRMS Thermal':<28} {self.style.WARNING('DEMO_MODE'):<18} Simulated Hotspots Active")
            else:
                self.stdout.write(f"{'NASA FIRMS Thermal':<28} {self.style.NOTICE('UNAVAILABLE'):<18} Upstream Server Busy")
        except Exception as e:
            self.stdout.write(f"{'NASA FIRMS Thermal':<28} {self.style.ERROR('ERROR'):<18} {type(e).__name__}")

        # 6. OpenStreetMap Overpass
        try:
            from services.osm_service import osm_service
            osm_res = osm_service.query_infrastructure(20.2961, 85.8245, 3000)
            if osm_res and osm_res.get('status') == 'LIVE':
                self.stdout.write(f"{'OpenStreetMap / Overpass':<28} {self.style.SUCCESS('LIVE'):<18} {osm_res.get('count', 0)} Infrastructure Nodes Resolved")
            elif osm_res and osm_res.get('is_demo'):
                self.stdout.write(f"{'OpenStreetMap / Overpass':<28} {self.style.WARNING('DEMO_MODE'):<18} Simulated Facilities Active")
            else:
                self.stdout.write(f"{'OpenStreetMap / Overpass':<28} {self.style.NOTICE('UNAVAILABLE'):<18} Overpass Server Busy")
        except Exception as e:
            self.stdout.write(f"{'OpenStreetMap / Overpass':<28} {self.style.ERROR('ERROR'):<18} {type(e).__name__}")

        # 7. OSRM Routing Engine
        try:
            from services.osrm_service import osrm_service
            routes_res = osrm_service.calculate_evacuation_routes(20.2961, 85.8245, 20.3540, 85.8180)
            if isinstance(routes_res, dict) and routes_res.get('status') == 'LIVE':
                routes_list = routes_res.get('routes', [])
                primary_dist = routes_list[0].get('distance_km') if routes_list else 'Live'
                self.stdout.write(f"{'OSRM Routing Engine':<28} {self.style.SUCCESS('LIVE'):<18} {len(routes_list)} Routes Calculated (Primary: {primary_dist} km)")
            elif isinstance(routes_res, dict) and routes_res.get('status') == 'UNAVAILABLE':
                self.stdout.write(f"{'OSRM Routing Engine':<28} {self.style.NOTICE('UNAVAILABLE'):<18} OSRM Server Busy")
            elif isinstance(routes_res, dict) and routes_res.get('is_demo'):
                self.stdout.write(f"{'OSRM Routing Engine':<28} {self.style.WARNING('DEMO_MODE'):<18} Simulated Routes Active")
            else:
                self.stdout.write(f"{'OSRM Routing Engine':<28} {self.style.NOTICE('AVAILABLE'):<18} Engine Reachable")
        except Exception as e:
            self.stdout.write(f"{'OSRM Routing Engine':<28} {self.style.ERROR('ERROR'):<18} {type(e).__name__}")

        # 8. ML Flood Risk Model
        try:
            from ml.risk_prediction.model import risk_predictor
            if risk_predictor.is_real_model:
                self.stdout.write(f"{'Odisha Flood Risk ML':<28} {self.style.SUCCESS('LOADED'):<18} Real XGBoost + Random Forest (14 Features)")
            elif getattr(settings, 'DEMO_MODE', False):
                self.stdout.write(f"{'Odisha Flood Risk ML':<28} {self.style.WARNING('DEMO_FALLBACK'):<18} Synthetic Baseline")
            else:
                self.stdout.write(f"{'Odisha Flood Risk ML':<28} {self.style.NOTICE('UNAVAILABLE'):<18} Real Model Not Found")
        except Exception as e:
            self.stdout.write(f"{'Odisha Flood Risk ML':<28} {self.style.ERROR('ERROR'):<18} {type(e).__name__}")

        self.stdout.write("----------------------------------------------------------------------")
        self.stdout.write(self.style.SUCCESS("[OK] Service telemetry check complete."))
