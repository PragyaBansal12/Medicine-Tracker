import json
from django.core.management.base import BaseCommand
import datetime
from django.utils import timezone
import time
from pywebpush import webpush, WebPushException
from medicines.models import Medication, PushSubscription, DoseLog
from django.conf import settings

class Command(BaseCommand):
    help = 'Run medication notifications in a single process'
    
    def handle(self, *args, **options):
        self.stdout.write(' Starting medication notification service...')
        
        while True:
            try:
                # Use timezone-aware datetime
                now = timezone.localtime(timezone.now())
                current_time = now.strftime("%H:%M")
                
                self.stdout.write(f"Current local time: {now}")
                self.stdout.write(f" Checking medications at {current_time}...")
                
                meds = Medication.objects.all()
                notified_count = 0
                
                for med in meds:
                    if med.times and current_time in med.times:
                        self.stdout.write(f" MATCH: {med.pill_name} at {current_time} for {med.user.username}")
                        
                        # Create scheduled datetime for today
                        scheduled_datetime = timezone.now().replace(
                            hour=int(current_time.split(':')[0]),
                            minute=int(current_time.split(':')[1]),
                            second=0,
                            microsecond=0
                        )
                        
                        # Check if DoseLog already exists
                        dose_log, created = DoseLog.objects.get_or_create(
                            medication=med,
                            user=med.user,
                            scheduled_time=scheduled_datetime,
                            defaults={'status': 'pending'}
                        )
                        
                        # Get all subscriptions for this user
                        subs = PushSubscription.objects.filter(user=med.user)
                        
                        # Send notification to all subscriptions
                        notification_sent = False
                        for sub in subs:
                            if not sub.p256dh or not sub.auth:
                                continue
                                
                            try:
                                # SIMPLE NOTIFICATION - No action buttons
                                webpush(
                                    subscription_info={
                                        "endpoint": sub.endpoint,
                                        "keys": {
                                            "p256dh": sub.p256dh,
                                            "auth": sub.auth
                                        }
                                    },
                                    data=json.dumps({
                                        "title": " Medicine Reminder",
                                        "body": f"Time to take {med.pill_name} ({med.dosage} mg)",
                                        "data": {
                                            "url": "/dashboard/"  # Always redirect to dashboard
                                        }
                                    }),
                                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                                    vapid_claims={"sub": "mailto:medication-tracker@example.com"}
                                )
                                notified_count += 1
                                notification_sent = True
                                self.stdout.write(f" Sent notification for {med.pill_name}")
                                break
                                
                            except WebPushException as e:
                                self.stdout.write(f" Error: {e}")
                                continue
                        
                        if not notification_sent:
                            self.stdout.write(f" Could not send notification for {med.pill_name}")
                
                self.stdout.write(f" TOTAL: Sent {notified_count} notifications at {current_time}")
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.stdout.write(" Stopping service...")
                break
            except Exception as e:
                self.stdout.write(f" Error: {e}")
                time.sleep(60)