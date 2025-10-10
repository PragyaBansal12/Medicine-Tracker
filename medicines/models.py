# medicines/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

FREQUENCY_CHOICES = [
    ("DAILY", "Daily"),
    ("WEEKLY", "Weekly"),
    ("MONTHLY", "Monthly"),
]

class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    pill_name = models.CharField(max_length=100)
    dosage = models.PositiveIntegerField(
        help_text="Dosage in milligrams",
        validators=[MaxValueValidator(10000)]
    )
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="DAILY")  
    times_per_day = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(24)])
    times = models.JSONField(default=list)
    
    # ⭐ CRUCIAL CHANGE: Now stores a list of Google Calendar Event IDs
    google_event_ids = models.JSONField(default=list, blank=True) 
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "N/A"
        return f"{self.pill_name} - {self.dosage} ({username})"

# --------------------------------------------------------------------------------------------------

class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.TextField()
    p256dh = models.TextField(default="")
    auth = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} subscription"
        
class NotificationLog(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    sent_date = models.DateField()  
    sent_time = models.CharField(max_length=5)  
    sent_at = models.DateTimeField(auto_now_add=True) 
    
    class Meta:
        unique_together = ['medication', 'sent_date', 'sent_time']
    
    def __str__(self):
        return f"{self.medication.pill_name} - {self.sent_time} on {self.sent_date}"
    
class DoseLog(models.Model):
    STATUS_CHOICES = (
        ('taken', 'Taken'),
        ('missed', 'Missed'),
    )

    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True) 
    scheduled_time = models.DateTimeField() 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        ordering = ['scheduled_time']

    def __str__(self):
        return f"{self.medication.pill_name} - {self.status} @ {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"  

class GoogleCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_uri = models.TextField(default="https://oauth2.googleapis.com/token")
    client_id = models.TextField()
    client_secret = models.TextField()
    scopes = models.TextField(default="https://www.googleapis.com/auth/calendar.events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Google credentials for {self.user.username}"