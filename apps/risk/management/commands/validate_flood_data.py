from django.core.management.base import BaseCommand
from ml.training import validate_raw_data

class Command(BaseCommand):
    help = "Validates raw data quality, coordinate bounds, temporal continuity, and class balance."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Running Odisha Flood Data Quality Audit..."))
        report = validate_raw_data.run()
        self.stdout.write(self.style.SUCCESS(f"[OK] Validation complete: {report['total_samples']:,} samples validated. Report saved to ml/data/validation/."))
