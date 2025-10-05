# medicines/management/commands/check_missed_doses.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from medicines.models import DoseLog
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get pending doses from 5+ minutes ago
        cutoff_time = timezone.now() - datetime.timedelta(minutes=5)
        
        # Find doses that are still pending and were scheduled more than 5 minutes ago
        missed_doses = DoseLog.objects.filter(
            status='pending',  # Assuming you add 'pending' status
            scheduled_time__lte=cutoff_time
        )
        
        missed_count = 0
        for dose in missed_doses:
            dose.status = 'missed'
            dose.save()
            missed_count += 1
            self.stdout.write(
                f"❌ Auto-marked as missed: {dose.medication.pill_name} at {dose.scheduled_time.strftime('%H:%M')}"
            )
        
        self.stdout.write(f"🎯 Marked {missed_count} doses as missed")