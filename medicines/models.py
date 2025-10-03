from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

FREQUENCY_CHOICES = [
    ("DAILY", "Daily"),
    ("WEEKLY", "Weekly"),
    ("MONTHLY", "Monthly"),
]

class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # link with user
    pill_name = models.CharField(max_length=100)
    dosage = models.PositiveIntegerField(
        help_text="Dosage in milligrams",
        validators=[MaxValueValidator(10000)]
    )
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="DAILY")  
    times_per_day = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(24)])
    times = models.JSONField(default=list)  # Store times as a list of strings
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pill_name} - {self.dosage} ({self.user.username})"

class DoseLog(models.Model):
    STATUS_CHOICES = (
        ('taken', 'Taken'),
        ('missed', 'Missed'),
    )

    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)  # record when user logged the dose
    scheduled_time = models.DateTimeField()  # full datetime of scheduled dose
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        ordering = ['scheduled_time']

    def __str__(self):
        return f"{self.medication.pill_name} - {self.status} @ {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"
