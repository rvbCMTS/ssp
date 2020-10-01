# Updates database format for SSP fluoro times
# Run as shell script: python manage.py shell < apps/fluoro_times/update_SSP_format.py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ssp.settings")

from apps.fluoro_times.models import Exam, Exposure

# All SSP fluoro times
for e in Exam.objects.filter(exam_no__icontains ='SSP'):
    query = Exposure.objects.get_or_create(
        exam=e,
        dirty_modality=e.dirty_modality,
        fluoro_time=e.fluoro_time,
        fluoro_time_minutes=e.fluoro_time_minutes,
        fluoro_time_seconds=e.fluoro_time_seconds,
        dose=e.dose
    )

print('done')