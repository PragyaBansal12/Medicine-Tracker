from django.core.management.base import BaseCommand
import datetime
import time
from pywebpush import webpush, WebPushException
from medicines.models import Medication, PushSubscription
from django.conf import settings

class Command(BaseCommand):
    help = 'Run medication notifications in a single process'
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting medication notification service (single process)...')
        
        while True:
            try:
                # Use simple local time
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M")
                
                self.stdout.write(f"🕒 Current local time: {now}")
                self.stdout.write(f"🔔 Checking medications at {current_time}...")
                
                meds = Medication.objects.all()
                notified_medications = set()  # To track which meds have been notified
                notified_count = 0
                
                for med in meds:
                    if med.times and current_time in med.times:
                        # Create unique key for medication + time
                        med_key = f"{med.id}_{current_time}"
                        
                        if med_key in notified_medications:
                            self.stdout.write(f"⏭️ Skipping {med.pill_name} - already notified this medication")
                            continue
                            
                        self.stdout.write(f"💊 MATCH: {med.pill_name} at {current_time} for {med.user.username}")
                        
                        subs = PushSubscription.objects.filter(user=med.user)
                        self.stdout.write(f"   Found {subs.count()} subscriptions for {med.user.username}")
                        
                        notification_sent = False
                        for sub in subs:
                            if not sub.p256dh or not sub.auth:
                                continue
                                
                            try:
                                webpush(
                                    subscription_info={
                                        "endpoint": sub.endpoint,
                                        "keys": {
                                            "p256dh": sub.p256dh,
                                            "auth": sub.auth
                                        }
                                    },
                                    data=f"Time to take {med.pill_name} ({med.dosage} mg)",
                                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                                    vapid_claims={"sub": "mailto:medication-tracker@example.com"}
                                )
                                notified_count += 1
                                notification_sent = True
                                self.stdout.write(f"✅ Sent notification for {med.pill_name} to {med.user.username}")
                                break
                                
                            except WebPushException:
                                continue
                        
                        # Mark this specific medication as notified
                        if notification_sent:
                            notified_medications.add(med_key)
                        else:
                            self.stdout.write(f"⚠️ Could not send notification for {med.pill_name}")
                
                self.stdout.write(f"🎯 TOTAL: Sent {notified_count} notifications for {len(notified_medications)} medications at {current_time}")
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.stdout.write("🛑 Stopping medication notification service...")
                break
            except Exception as e:
                self.stdout.write(f"🚨 Unexpected error: {e}")
                time.sleep(60)