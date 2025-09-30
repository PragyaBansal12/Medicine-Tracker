from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

FREQUENCY_CHOICES = [
    ("DAILY", "Daily"),
    ("WEEKLY", "Weekly"),
    ("MONTHLY", "Monthly"),
]

class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)   # link with user
    pill_name = models.CharField(max_length=100)
    dosage = models.PositiveIntegerField(
        help_text="Dosage in milligrams",
        validators=[MaxValueValidator(10000)]
    )   # quantity
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="DAILY")  
    time_per_day = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(24)])
    times = models.JSONField(default=list)  # Store times as a list of strings
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pill_name} - {self.dosage} ({self.user.username})"



