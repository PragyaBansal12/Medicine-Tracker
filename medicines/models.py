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
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    pill_name = models.CharField(max_length=100)
    dosage = models.PositiveIntegerField(
        help_text="Dosage in milligrams",
        validators=[MaxValueValidator(10000)]
    )
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="DAILY")  
    times_per_day = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(24)])
    times = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pill_name} - {self.dosage} ({self.user.username})"

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
        # unique notif
        unique_together = ['medication', 'sent_date', 'sent_time']
    
    def __str__(self):
        return f"{self.medication.pill_name} - {self.sent_time} on {self.sent_date}"