from django.core.management.base import BaseCommand
from ml.training import evaluate

class Command(BaseCommand):
    help = "Evaluates trained models on holdout test set, generating metrics and validation reports."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Running Odisha Flood Model Evaluation Suite..."))
        metrics = evaluate.run()
        self.stdout.write(self.style.SUCCESS("[OK] Model evaluation report generated. Results stored in ml/data/validation/."))
