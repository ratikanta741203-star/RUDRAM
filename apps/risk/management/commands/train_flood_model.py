from django.core.management.base import BaseCommand
from ml.training import train

class Command(BaseCommand):
    help = "Trains real XGBoost and Random Forest classifiers on Odisha historical flood dataset."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting Real XGBoost + Random Forest Training..."))
        meta = train.run()
        self.stdout.write(self.style.SUCCESS(f"[OK] Real models trained and saved to ml/models/ successfully (Ensemble Accuracy: {meta['test_metrics']['ensemble']['accuracy']*100:.2f}%, Recall: {meta['test_metrics']['ensemble']['recall']*100:.2f}%)."))
