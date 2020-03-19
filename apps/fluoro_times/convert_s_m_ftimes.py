# Convert seconds and minutes fields to flurotime [seconds]
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ssp.settings")

from apps.fluoro_times.models import Exam

# All fluoro times from Orbit, SSP fluoro times already in seconds
for e in Exam.objects.exclude(exam_no__icontains ='SSP'):
    e.fluoro_time = e.fluoro_time_minutes*60 + e.fluoro_time_seconds
    e.save()

print('done')