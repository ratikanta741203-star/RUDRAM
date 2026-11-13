"""
Django Management Command: python manage.py train_cyclone_model
Builds historical cyclone dataset v2, trains candidate ML models, evaluates performance,
and updates active production model registry if candidate outperforms baseline.
"""
from django.core.management.base import BaseCommand
from ml.training.build_enhanced_datasets import build_cyclone_dataset
from ml.training.train_enhanced_models import train_enhanced_cyclone_models

class Command(BaseCommand):
    help = 'Trains, evaluates, and registers historical cyclone risk ML models (XGBoost Regressor v2).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting RUDRAM Historical Cyclone Model Training Pipeline..."))
        build_cyclone_dataset()
        report, _ = train_enhanced_cyclone_models()
        self.stdout.write(self.style.SUCCESS(
            f"Successfully trained cyclone models! Candidate MAE: {report['candidate_metrics']['xgboost_v2']['mae']}, "
            f"R²: {report['candidate_metrics']['xgboost_v2']['r2']}. "
            f"Promoted to active: {report['promoted_to_active']}"
        ))
