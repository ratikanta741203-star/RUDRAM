from django.core.management.base import BaseCommand
from ml.training import build_training_dataset

class Command(BaseCommand):
    help = "Builds preprocessed and feature-engineered training matrix in Parquet & CSV formats."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Building Odisha Flood Training Matrix..."))
        df = build_training_dataset.run()
        self.stdout.write(self.style.SUCCESS(f"[OK] Training dataset built successfully with {len(df):,} samples and {len(df.columns)} features."))
