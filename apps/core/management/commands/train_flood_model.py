"""
Django Management Command: python manage.py train_flood_model
Builds historical flood dataset v2, trains candidate ML models, evaluates performance,
and updates active production model registry if candidate outperforms baseline.
"""
from django.core.management.base import BaseCommand
from ml.training.build_enhanced_datasets import build_enhanced_flood_dataset
from ml.training.train_enhanced_models import train_enhanced_flood_models

class Command(BaseCommand):
    help = 'Trains, evaluates, and registers historical flood risk ML models (XGBoost & Random Forest v2).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting RUDRAM Historical Flood Model Training Pipeline..."))
        build_enhanced_flood_dataset()
        report, _, _ = train_enhanced_flood_models()
        self.stdout.write(self.style.SUCCESS(
            f"Successfully trained flood models! Candidate F1: {report['candidate_metrics']['xgboost_v2']['f1_score']}, "
            f"ROC-AUC: {report['candidate_metrics']['xgboost_v2']['roc_auc']}. "
            f"Promoted to active: {report['promoted_to_active']}"
        ))
