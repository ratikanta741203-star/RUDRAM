from apps.disasters.models import Disaster, DisasterTimeline
from apps.risk.models import RiskPrediction, RiskZone
from apps.shelters.models import Shelter
from apps.resources.models import Resource, ResourceAllocation, RescueTeam
from apps.alerts.models import Alert
from apps.assistant.models import EmergencyRecommendation
from apps.satellite.models import SatelliteAnalysis
from apps.weather.models import WeatherObservation, RainfallObservation
from apps.infrastructure.models import Infrastructure, River, Dam, Bridge
from apps.population.models import PopulationExposure
from apps.core.models import DataSourceStatus

class FloodEmergencyDemoEngine:
    """
    RUDRAM 12-Step Flood Emergency Demonstration Engine.
    Executes an end-to-end disaster scenario in Bhubaneswar, Odisha.
    """

    def run_scenario(self, intensity="CRITICAL"):
        # Step 1: Simulate heavy monsoon rainfall & rising river levels
        WeatherObservation.objects.create(
            station_name='Bhubaneswar IMD Observatory',
            latitude=20.2961,
            longitude=85.8245,
            temperature_c=27.5,
            humidity_pct=94.0,
            rainfall_current_mm=32.5,
            rainfall_24h_mm=215.0,
            wind_speed_kmh=48.0,
            weather_condition='Torrential Monsoon Inundation & Squall Winds',
            source='Open-Meteo & IMD Radar Station',
            is_demo=True
        )

        RainfallObservation.objects.create(
            location_name='Bhubaneswar Central Basin',
            latitude=20.2961,
            longitude=85.8245,
            rainfall_1h_mm=32.5,
            rainfall_3h_mm=88.0,
            rainfall_6h_mm=142.0,
            rainfall_12h_mm=186.0,
            rainfall_24h_mm=215.0,
            rainfall_7d_mm=420.0,
            source='GPM IMERG & Ground Gauges (Simulated)'
        )

        # Step 2: Update river water level to near danger mark
        River.objects.filter(name__icontains='Kuakhai').update(
            current_water_level_m=14.85,
            danger_level_m=15.0,
            trend='CRITICAL RISING (+0.25 m/hr)'
        )
        River.objects.filter(name__icontains='Daya').update(
            current_water_level_m=15.20,
            danger_level_m=15.0,
            trend='OVERFLOWING EMBANKMENT (+0.30 m/hr)'
        )

        # Step 3: Trigger active disaster event
        disaster, _ = Disaster.objects.get_or_create(
            title="Bhubaneswar Urban & Deltaic Flash Flood Emergency",
            defaults={
                'disaster_type': 'FLOOD',
                'severity': 'CRITICAL',
                'status': 'ACTIVE',
                'location_name': 'Bhubaneswar Urban & Riverine Catchment',
                'state': 'Odisha',
                'district': 'Khordha',
                'latitude': 20.2961,
                'longitude': 85.8245,
                'radius_km': 14.5,
                'affected_area_sqkm': 48.6,
                'exposed_population': 21400,
                'risk_score': 91,
                'rainfall_24h_mm': 215.0,
                'river_water_level_m': 14.85,
                'danger_water_level_m': 15.0,
                'description': 'Severe multi-catchment riverine overflow from Kuakhai and Daya rivers combined with urban stormwater drainage backing up.',
                'is_demo': True
            }
        )
        disaster.risk_score = 91
        disaster.severity = 'CRITICAL'
        disaster.status = 'ACTIVE'
        disaster.save()

        # Step 4: Add timeline entry
        DisasterTimeline.objects.create(
            disaster=disaster,
            title='Daya River Embankment Breach Alert',
            description='Water level surpassed 15.2m danger mark at Sundarpada gauge station. Immediate evacuation ordered for low-lying sectors.',
            severity_level='CRITICAL',
            action_taken='Emergency siren broadcast, ODRAF Unit 1 dispatched, safe routes published'
        )

        # Step 5: Create Critical Alert
        Alert.objects.create(
            disaster=disaster,
            title='EMERGENCY: Daya River Embankment Breach Alert (Red Warning)',
            message='Severe inundation underway in Sundarpada & Rasulgarh low-lying sectors. Water level rising fast. Evacuate via Janpath Bypass Ridge (Route B).',
            severity='CRITICAL',
            disaster_type='FLOOD',
            location_name='Sundarpada & Rasulgarh Lowlands',
            latitude=20.2961,
            longitude=85.8245,
            recommended_action='Proceed immediately to BJB College High-Ground Shelter or Capital High School Shelter. Avoid all submerged culverts.',
            source='RUDRAM Automated Multi-Hazard Early Warning Engine'
        )

        # Step 6: Trigger AI Emergency Assistant Directives
        EmergencyRecommendation.objects.create(
            disaster=disaster,
            situation_summary='CRITICAL SITUATION: AI Model detects 91% flood probability with imminent breach flow along Daya riverbank.',
            priority='CRITICAL',
            action_items=[
                {'action': 'Direct evacuees to BJB College Shelter (Capacity: 1,200, Available: 750)', 'priority': 'P0 (Immediate)'},
                {'action': 'Barricade Daya River Road (0.9m submerged depth)', 'priority': 'P0 (Immediate)'},
                {'action': 'Deploy 2x ODRAF rescue inflatable boats at Sundarpada Canal', 'priority': 'P1 (30 Mins)'},
                {'action': 'Dispatch 2,000 drinking water canisters and emergency ORS kits', 'priority': 'P1 (45 Mins)'}
            ],
            rationale='Ground saturation index is 0.94; flood wave travel time estimated under 90 minutes.',
            is_rule_based_demo=True
        )

        return {
            'success': True,
            'message': '12-Step Flood Emergency Demonstration Scenario successfully initialized.',
            'disaster_id': disaster.id,
            'risk_score': 91,
            'severity': 'CRITICAL',
            'location': 'Bhubaneswar, Odisha'
        }

demo_engine = FloodEmergencyDemoEngine()
