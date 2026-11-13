from django.core.management.base import BaseCommand
from apps.disasters.models import Disaster, DisasterTimeline
from apps.shelters.models import Shelter
from apps.resources.models import Resource, ResourceAllocation, RescueTeam
from apps.infrastructure.models import Infrastructure, River, Dam, Bridge
from apps.population.models import PopulationExposure
from apps.alerts.models import Alert
from apps.assistant.models import EmergencyRecommendation
from apps.satellite.models import SatelliteAnalysis
from apps.fire.models import FireHotspot

class Command(BaseCommand):
    help = "Safely removes seeded demo datasets while preserving users, RBAC roles, database schemas, and real records."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=================================================="))
        self.stdout.write(self.style.NOTICE("[RUDRAM] Removing Seeded Demo Database Records"))
        self.stdout.write(self.style.NOTICE("=================================================="))

        # 1. Rivers, Dams, Bridges
        rivers_del, _ = River.objects.filter(is_demo=True).delete()
        dams_del, _ = Dam.objects.filter(is_demo=True).delete()
        bridges_del, _ = Bridge.objects.filter(is_demo=True).delete()
        self.stdout.write(f"  [+] Cleared Demo Hydro & River Gauge Records: {rivers_del + dams_del + bridges_del} objects")

        # 2. Critical Infrastructure
        infra_del, _ = Infrastructure.objects.filter(is_demo=True).delete()
        self.stdout.write(f"  [+] Cleared Demo Infrastructure Records: {infra_del} objects")

        # 3. Shelters
        shelters_del, _ = Shelter.objects.filter(is_demo=True).delete()
        self.stdout.write(f"  [+] Cleared Demo Shelter Records: {shelters_del} objects")

        # 4. Resources & Rescue Teams
        teams_del, _ = RescueTeam.objects.filter(
            lead_officer__in=['Major R. K. Mohapatra', 'Inspector A. K. Singh', 'Station Officer P. Jena', 'Dr. S. K. Das']
        ).delete()
        res_del, _ = Resource.objects.filter(
            warehouse_location__in=[
                'Central Warehouse Rasulgarh', 'Civil Supplies Godown Unit 2', 'AIIMS Medical Depot',
                'Red Cross Depot Bhubaneswar', 'ODRAF Base Camp Rasulgarh',
                'Disaster Action Force Motor Pool', 'BMC Mechanical Division Yard'
            ]
        ).delete()
        self.stdout.write(f"  [+] Cleared Demo Rescue Teams & Resources: {teams_del + res_del} objects")

        # 5. Population Exposure
        pop_del, _ = PopulationExposure.objects.filter(is_demo=True).delete()
        self.stdout.write(f"  [+] Cleared Demo Population Exposure Zones: {pop_del} objects")

        # 6. Disasters & Timelines
        disaster_del, _ = Disaster.objects.filter(is_demo=True).delete()
        self.stdout.write(f"  [+] Cleared Demo Disaster Incidents & Timelines: {disaster_del} objects")

        # 7. Demo Alerts
        alert_del, _ = Alert.objects.filter(
            source__icontains='Early Warning System',
            title__icontains='Daya & Kuakhai'
        ).delete()
        self.stdout.write(f"  [+] Cleared Demo Early Warning Alerts: {alert_del} objects")

        # 8. Demo Satellite Analysis
        sat_del, _ = SatelliteAnalysis.objects.filter(is_demo=True).delete()
        self.stdout.write(f"  [+] Cleared Demo Satellite Inundation Runs: {sat_del} objects")

        # 9. Demo AI Assistant Recommendations
        rec_del, _ = EmergencyRecommendation.objects.filter(is_rule_based_demo=True).delete()
        self.stdout.write(f"  [+] Cleared Demo AI Recommendations: {rec_del} objects")

        # 10. Demo Fire Hotspots
        fire_del, _ = FireHotspot.objects.filter(is_demo=True).delete()
        self.stdout.write(f"  [+] Cleared Demo Thermal Fire Hotspots: {fire_del} objects")

        self.stdout.write(self.style.SUCCESS("[OK] Demo database cleanup completed successfully. Users, RBAC permissions, and system configurations preserved."))
