# Convert fluoro_time to seperate seconds and minutes fields
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ssp.settings")

from apps.fluoro_times.models import Exam
from math import floor

# All fluoro times from Orbit
for e in Exam.objects.exclude(exam_no__icontains ='SSP'):
    e.fluoro_time_minutes = floor(e.fluoro_time)
    e.fluoro_time_seconds = (e.fluoro_time - floor(e.fluoro_time))*60
    e.save()

# All fluoro times from SSP
for e in Exam.objects.filter(exam_no__icontains ='SSP'):
    e.fluoro_time_minutes = floor(e.fluoro_time/60)
    e.fluoro_time_seconds = e.fluoro_time - floor(e.fluoro_time/60)*60
    e.save()

print('done')