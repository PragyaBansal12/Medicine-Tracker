from django.contrib import admin
from .models import Medication,DoseLog

admin.site.register(Medication)
admin.site.register(DoseLog)

