from django.db import models
from django.contrib.auth.models import User

class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)   # link with user
    pill_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)   # quantity
    time = models.TimeField()
    frequency = models.CharField(max_length=50)  # e.g. "Twice a day"

    def __str__(self):
        return f"{self.pill_name} - {self.dosage} ({self.user.username})"



