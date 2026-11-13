from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.disasters.models import Disaster, DisasterTimeline
from apps.risk.models import RiskZone, RiskPrediction
from apps.shelters.models import Shelter
from apps.resources.models import Resource, ResourceAllocation, RescueTeam
from apps.infrastructure.models import Infrastructure, River, Dam, Bridge
from apps.population.models import PopulationExposure
from apps.alerts.models import Alert
from apps.assistant.models import EmergencyRecommendation
from apps.satellite.models import SatelliteAnalysis
from apps.fire.models import FireHotspot
from apps.core.models import DataSourceStatus

class Command(BaseCommand):
    help = 'Seeds realistic, calibrated Bhubaneswar/Odisha demo datasets for RUDRAM hackathon demonstration.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('[RUDRAM] Starting database demo seeding...'))

        # 1. Ensure Superuser & Demo Users
        admin_user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@rudram.gov.in', 'is_staff': True, 'is_superuser': True})
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            profile = admin_user.profile
            profile.role = 'ADMIN'
            profile.organization = 'Odisha State Disaster Management Authority (OSDMA)'
            profile.save()
            self.stdout.write(self.style.SUCCESS('Created default superuser: admin / admin123'))

        operator_user, created = User.objects.get_or_create(username='operator', defaults={'email': 'operator@rudram.gov.in'})
        if created:
            operator_user.set_password('operator123')
            operator_user.save()
            profile = operator_user.profile
            profile.role = 'EMERGENCY_OPERATOR'
            profile.organization = 'Emergency Operations Command Centre'
            profile.save()

        # 2. Data Sources
        sources = [
            ('open_meteo', 'Open-Meteo Weather API', 'Meteorological', 'CONNECTED', 'https://api.open-meteo.com', True, 45.2),
            ('nasa_power', 'NASA POWER Climatology API', 'Climatology / Satellite', 'CONNECTED', 'https://power.larc.nasa.gov', True, 82.1),
            ('gpm_imerg', 'NASA GPM IMERG Satellite Rainfall', 'Remote Sensing', 'DEMO', 'https://gpm.nasa.gov/data/imerg', False, 0.0),
            ('srtm_dem', 'SRTM 30m Global Elevation Model', 'Terrain & Hydrology', 'CONNECTED', 'Local Terrain Processing Engine', True, 12.0),
            ('google_earth_engine', 'Google Earth Engine & Sentinel-1/2', 'Earth Observation / Radar', 'DEMO', 'https://earthengine.googleapis.com', False, 0.0),
            ('overpass', 'OpenStreetMap Overpass API', 'GIS & Infrastructure', 'CONNECTED', 'https://overpass-api.de/api/interpreter', True, 120.5),
            ('osrm', 'OSRM Routing Engine', 'Evacuation / Routing', 'CONNECTED', 'https://router.project-osrm.org', True, 95.0),
            ('nasa_firms', 'NASA FIRMS Fire Hotspots', 'Thermal Remote Sensing', 'DEMO', 'https://firms.modaps.eosdis.nasa.gov', False, 0.0),
        ]
        for sname, dname, cat, st, ep, live, rtime in sources:
            DataSourceStatus.objects.update_or_create(
                source_name=sname,
                defaults={
                    'display_name': dname,
                    'category': cat,
                    'status': st,
                    'endpoint_url': ep,
                    'is_live': live,
                    'response_time_ms': rtime
                }
            )

        # 3. Rivers & Dams
        River.objects.update_or_create(
            name='Kuakhai River',
            defaults={
                'basin': 'Mahanadi Deltaic System',
                'current_water_level_m': 14.35,
                'warning_level_m': 13.80,
                'danger_level_m': 15.00,
                'trend': 'RISING (+0.18 m/hr)',
                'is_demo': True
            }
        )
        River.objects.update_or_create(
            name='Daya River',
            defaults={
                'basin': 'Mahanadi Deltaic System',
                'current_water_level_m': 14.80,
                'warning_level_m': 14.00,
                'danger_level_m': 15.00,
                'trend': 'RAPID SWELL (+0.22 m/hr)',
                'is_demo': True
            }
        )
        Dam.objects.update_or_create(
            name='Hirakud Reservoir Dam',
            defaults={
                'river_name': 'Mahanadi Main Stem',
                'latitude': 21.5700,
                'longitude': 83.8700,
                'current_reservoir_level_ft': 628.6,
                'full_reservoir_level_ft': 630.0,
                'inflow_cusecs': 485000,
                'outflow_cusecs': 440000,
                'gates_open': 24,
                'total_gates': 64,
                'status_alert': 'STAGE 2 FLOOD DISCHARGE',
                'is_demo': True
            }
        )
        Bridge.objects.update_or_create(
            name='Kuakhai Road Bridge (NH 16)',
            defaults={
                'river_crossed': 'Kuakhai River',
                'latitude': 20.3125,
                'longitude': 85.8492,
                'clearance_above_water_m': 1.6,
                'is_passable': True,
                'structural_alert': 'Approaches Wet - Heavy Vehicle Caution',
                'is_demo': True
            }
        )

        # 4. Critical Infrastructure
        infra_items = [
            ('AIIMS Bhubaneswar Hospital', 'HOSPITAL', 20.2312, 85.7765, 950, '0674-2476789', True, 36.0),
            ('Capital Hospital Unit 6', 'HOSPITAL', 20.2721, 85.8192, 600, '0674-2391983', True, 28.5),
            ('KIMS Super Specialty Hospital', 'HOSPITAL', 20.3540, 85.8180, 800, '0674-2725182', True, 42.0),
            ('Odisha Fire & Disaster Response Academy', 'FIRE_STATION', 20.2850, 85.8450, 150, '101 / 112', True, 29.0),
            ('Kalpana Square Fire Station', 'FIRE_STATION', 20.2610, 85.8420, 80, '101 / 112', True, 24.0),
            ('Khandagiri Police Sub-Division', 'POLICE', 20.2580, 85.7860, 60, '112', True, 34.0),
            ('Saheed Nagar Police Station', 'POLICE', 20.2920, 85.8520, 50, '112', True, 26.0),
            ('Bhubaneswar 220kV Grid Substation', 'POWER_STATION', 20.3010, 85.8650, 0, '0674-2541200', True, 25.0),
        ]
        for name, itype, lat, lon, cap, phone, gen, elev in infra_items:
            Infrastructure.objects.update_or_create(
                name=name,
                defaults={
                    'infra_type': itype,
                    'latitude': lat,
                    'longitude': lon,
                    'capacity': cap,
                    'contact_phone': phone,
                    'is_backup_power_ready': gen,
                    'elevation_m': elev,
                    'is_demo': True
                }
            )

        # 5. Shelters
        shelters_data = [
            ('BJB Autonomous College Multipurpose Shelter', 'BJB Nagar, Bhubaneswar', 20.2545, 85.8390, 1200, 420, True, True, True, True, True, 'OPEN', 32.0),
            ('Capital High School Relief Centre', 'Unit 3, Kharavela Nagar', 20.2780, 85.8420, 800, 310, True, True, True, True, True, 'OPEN', 30.5),
            ('Utkal University Indoor Stadium Shelter', 'Vani Vihar Campus', 20.3015, 85.8580, 1500, 480, True, True, True, True, True, 'OPEN', 34.0),
            ('Patia Cyclone & Emergency Shelter', 'Patia Square Sector 5', 20.3580, 85.8210, 1000, 150, True, True, True, True, True, 'OPEN', 44.0),
            ('Sundarpada Primary School Camp', 'Old Town Flood Fringe', 20.2380, 85.8260, 500, 490, True, True, False, False, False, 'FULL', 16.0),
        ]
        for name, addr, lat, lon, cap, occ, w, f, m, g, da, st, elev in shelters_data:
            Shelter.objects.update_or_create(
                name=name,
                defaults={
                    'address': addr,
                    'latitude': lat,
                    'longitude': lon,
                    'total_capacity': cap,
                    'current_occupancy': occ,
                    'has_potable_water': w,
                    'has_food_stocks': f,
                    'has_medical_station': m,
                    'has_backup_generator': g,
                    'has_disability_access': da,
                    'status': st,
                    'elevation_m': elev,
                    'is_demo': True
                }
            )

        # 6. Resources & Rescue Teams
        resources_data = [
            ('Potable Drinking Water (20L Jerry Cans)', 'WATER', 6400, 10000, 2400, 'Canisters', 'Central Warehouse Rasulgarh'),
            ('Ready-to-Eat Dry Ration Packets (Chuda/Gur/Biscuits)', 'FOOD', 8200, 12000, 3500, 'Packets', 'Civil Supplies Godown Unit 2'),
            ('Emergency First-Aid & Anti-Venom Kits', 'MEDICINE', 1450, 2000, 450, 'Kits', 'AIIMS Medical Depot'),
            ('Waterproof Tarpaulins & Sleeping Mats', 'BLANKETS', 3800, 6000, 1800, 'Kits', 'Red Cross Depot Bhubaneswar'),
            ('Inflatable Motorized Rescue Boats (Zodiac 8-Man)', 'RESCUE_BOATS', 18, 25, 12, 'Boats', 'ODRAF Base Camp Rasulgarh'),
            ('Amphibious All-Terrain Rescue Trucks (4x4)', 'VEHICLES', 14, 18, 8, 'Trucks', 'Disaster Action Force Motor Pool'),
            ('High-Discharge Dewatering Diesel Pumps (50HP)', 'PUMPS', 32, 45, 20, 'Pumps', 'BMC Mechanical Division Yard'),
        ]
        for name, cat, avail, req, alloc, unit, loc in resources_data:
            Resource.objects.update_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'quantity_available': avail,
                    'quantity_required': req,
                    'quantity_allocated': alloc,
                    'unit': unit,
                    'warehouse_location': loc
                }
            )

        teams_data = [
            ('ODRAF Unit 1 (Bhubaneswar Rapid Taskforce)', 'ODRAF', 32, 'Major R. K. Mohapatra', '94370-11201', 'DEPLOYED', 20.2961, 85.8245, '4 Zodiac boats, underwater sonar, emergency lighting'),
            ('NDRF 3rd Battalion (Strike Team Alpha)', 'NDRF', 45, 'Inspector A. K. Singh', '94370-11202', 'AVAILABLE', 20.2650, 85.7950, '8 Motor boats, satellite comms, canine search unit'),
            ('Bhubaneswar Central Fire & Rescue Unit', 'FIRE_RESCUE', 28, 'Station Officer P. Jena', '94370-11203', 'DEPLOYED', 20.2610, 85.8420, 'Amphibious tender, rope-rescue systems, de-watering rigs'),
            ('Mobile Trauma & Medical Response Unit 4', 'MEDICAL_RAPID', 16, 'Dr. S. K. Das', '94370-11204', 'AVAILABLE', 20.2312, 85.7765, '4 Mobile ICU ambulances, emergency trauma surgeons'),
        ]
        for name, ttype, cnt, officer, phone, st, lat, lon, equip in teams_data:
            RescueTeam.objects.update_or_create(
                name=name,
                defaults={
                    'team_type': ttype,
                    'members_count': cnt,
                    'lead_officer': officer,
                    'contact_phone': phone,
                    'status': st,
                    'latitude': lat,
                    'longitude': lon,
                    'equipment_summary': equip
                }
            )

        # 7. Population Exposure
        pop_zones = [
            ('Rasulgarh Lowland Embankment Zone', 20.2980, 85.8640, 48000, 9200, 2800, 1800, 5200.0, 88),
            ('Sundarpada-Old Town Drainage Basin', 20.2450, 85.8250, 36000, 6800, 2100, 1200, 4400.0, 82),
            ('Acharya Vihar - Nayapalli Storm Channel', 20.3010, 85.8320, 42000, 2400, 650, 200, 3800.0, 54),
        ]
        for zname, lat, lon, tot, exp, vul, crit, dens, score in pop_zones:
            PopulationExposure.objects.update_or_create(
                zone_name=zname,
                defaults={
                    'latitude': lat,
                    'longitude': lon,
                    'total_population': tot,
                    'exposed_population': exp,
                    'vulnerable_population': vul,
                    'critical_risk_population': crit,
                    'density_per_sqkm': dens,
                    'exposure_score': score,
                    'source': 'WorldPop / Census of India Baseline',
                    'is_demo': True
                }
            )

        # 8. Disaster Event & Initial Timeline
        disaster, _ = Disaster.objects.get_or_create(
            title="Bhubaneswar Urban & Riverine Monsoon Flood Emergency",
            defaults={
                'disaster_type': 'FLOOD',
                'severity': 'CRITICAL',
                'status': 'ACTIVE',
                'location_name': 'Bhubaneswar Catchment & Deltaic Basin',
                'state': 'Odisha',
                'district': 'Khordha',
                'latitude': 20.2961,
                'longitude': 85.8245,
                'radius_km': 14.0,
                'affected_area_sqkm': 45.8,
                'exposed_population': 18400,
                'risk_score': 84,
                'rainfall_24h_mm': 186.4,
                'river_water_level_m': 14.35,
                'danger_water_level_m': 15.00,
                'description': 'Continuous monsoon depression rainfall causing severe backflow in Daya and Kuakhai river branches.',
                'is_demo': True
            }
        )

        DisasterTimeline.objects.get_or_create(
            disaster=disaster,
            title='Flood Incident Room Activated',
            defaults={
                'description': '24-hour rainfall crossed 180mm. Automated AI Risk Model predicted 84% flood probability.',
                'severity_level': 'HIGH',
                'action_taken': 'Emergency control room activated; first alerts issued'
            }
        )

        # 9. Alerts
        Alert.objects.get_or_create(
            title='CRITICAL FLASH FLOOD WARNING: Daya & Kuakhai River Basin',
            defaults={
                'disaster': disaster,
                'message': 'Severe rainfall accumulation (186.4mm). High river discharge approaching danger level 15.0m.',
                'severity': 'CRITICAL',
                'disaster_type': 'FLOOD',
                'location_name': 'Bhubaneswar Urban & Low-Lying Riverine Fringe',
                'latitude': 20.2961,
                'longitude': 85.8245,
                'recommended_action': 'Move vulnerable population to high-ground shelters. Avoid submerged Daya Embankment road.',
                'is_active': True,
                'source': 'RUDRAM AI Multi-Hazard Early Warning System'
            }
        )

        # 10. Satellite Initial Record
        SatelliteAnalysis.objects.get_or_create(
            title='Sentinel-1 SAR C-Band Rapid Inundation Analysis',
            defaults={
                'sensor': 'SENTINEL_1',
                'status': 'COMPLETED',
                'aoi_name': 'Bhubaneswar Floodplain Delta',
                'pre_event_date': '2026-08-01',
                'post_event_date': '2026-08-14',
                'flooded_area_sqkm': 28.4,
                'damaged_area_sqkm': 34.8,
                'affected_population': 16200,
                'submerged_roads_km': 24.6,
                'confidence': 0.93,
                'is_demo': True
            }
        )

        # 11. Initial AI Emergency Recommendation
        EmergencyRecommendation.objects.get_or_create(
            disaster=disaster,
            priority='CRITICAL',
            defaults={
                'situation_summary': 'CRITICAL FLOOD RISK: AI Model calculated 84% flood risk with 186.4mm precipitation and saturated catchment.',
                'action_items': [
                    {'action': 'Issue evacuation directive for Daya Embankment and Rasulgarh low-lying zone', 'priority': 'P0'},
                    {'action': 'Direct evacuees to BJB Autonomous College Shelter (Capacity: 1,200, Available: 780)', 'priority': 'P0'},
                    {'action': 'Route traffic through Janpath Bypass Ridge (Route B - 94% Safety Score)', 'priority': 'P0'},
                    {'action': 'Deploy ODRAF Unit 1 with inflatable boats at Sundarpada canal staging point', 'priority': 'P1'},
                    {'action': 'Dispatch 1,500 dry food packets and 3,000L potable water canisters', 'priority': 'P1'}
                ],
                'rationale': 'Rapid rise of river gauge (+0.18m/hr) indicates embankment overflow vulnerability within 3 hours.',
                'is_rule_based_demo': True
            }
        )

        # 12. Fire Hotspots
        FireHotspot.objects.get_or_create(
            latitude=20.4161,
            longitude=85.7445,
            defaults={
                'brightness': 338.4,
                'confidence': 88,
                'satellite': 'VIIRS NOAA-20',
                'frp_mw': 28.5,
                'hotspot_type': 'Chandaka Forest Fringe Biomass Burning',
                'is_demo': True
            }
        )

        self.stdout.write(self.style.SUCCESS('[RUDRAM] Bhubaneswar/Odisha realistic demo datasets seeded successfully!'))
