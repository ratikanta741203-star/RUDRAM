"""
Django Management Command: python manage.py train_all_models
Executes complete historical dataset creation, ML model training, validation,
model registry update, and quality report generation for Flood & Cyclone models.
"""
from django.core.management.base import BaseCommand
from ml.training.build_enhanced_datasets import build_cyclone_dataset, build_enhanced_flood_dataset
from ml.training.train_enhanced_models import run_all_training

class Command(BaseCommand):
    help = 'Executes complete end-to-end historical ML training, evaluation, and model registry promotion.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== Starting RUDRAM Master ML Model Retraining Engine ==="))
        self.stdout.write("1. Building versioned historical datasets (v2)...")
        build_cyclone_dataset()
        build_enhanced_flood_dataset()

        self.stdout.write("2. Training candidate models, evaluating held-out test sets, and registering active models...")
        run_all_training()

        self.stdout.write(self.style.SUCCESS("=== RUDRAM ML Retraining Completed Successfully! ==="))
