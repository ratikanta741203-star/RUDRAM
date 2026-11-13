from django.core.management.base import BaseCommand
from services.gee_service import gee_service

class Command(BaseCommand):
    help = "Tests Google Earth Engine configuration, Service Account JSON credential existence, and Earth Engine authentication."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=================================================="))
        self.stdout.write(self.style.NOTICE("[RUDRAM] Google Earth Engine Configuration Check"))
        self.stdout.write(self.style.NOTICE("=================================================="))

        status_info = gee_service.get_connection_status()

        self.stdout.write(f"[RUDRAM] GEE Enabled: {status_info['enabled']}")
        self.stdout.write(f"[RUDRAM] Project ID: {status_info['project_id']}")
        self.stdout.write(f"[RUDRAM] Service Account: {status_info['service_account']}")
        
        if status_info['credential_file_found']:
            self.stdout.write(self.style.SUCCESS("[RUDRAM] Credential File: FOUND (secrets/gee-service-account.json)"))
        else:
            self.stdout.write(self.style.WARNING("[RUDRAM] Credential File: NOT FOUND (Place service account JSON at secrets/gee-service-account.json)"))

        if status_info['authenticated']:
            self.stdout.write(self.style.SUCCESS("[RUDRAM] Earth Engine Authentication: SUCCESS (Live Copernicus Sentinel Access Active)"))
        else:
            self.stdout.write(self.style.NOTICE("[RUDRAM] Earth Engine Authentication: FALLBACK ACTIVE (Operating in High-Fidelity Simulation Lab)"))

        self.stdout.write(self.style.SUCCESS("[OK] GEE configuration check complete."))
