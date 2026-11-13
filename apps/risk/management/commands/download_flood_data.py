from django.core.management.base import BaseCommand
from ml.training import download_data

class Command(BaseCommand):
    help = "Downloads and assembles raw historical meteorological, DEM, and flood occurrence datasets for Odisha (2005-2024)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Executing Odisha Flood Raw Data Harvester..."))
        download_data.run()
        self.stdout.write(self.style.SUCCESS("[OK] Raw datasets successfully assembled in ml/data/raw/."))
