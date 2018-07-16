from django.urls import path
from .views import mgqa_measurement_form, mgqa_measurement_result, MGQAMeasurementForm, MGQAResultView

app_name = 'mammography'
urlpatterns = [
    path('', mgqa_measurement_result, name='mg-weekly-qa-result'),
    path('veckoqa', mgqa_measurement_form, name='mg-weekly-measurement'),
    path('api/update-weekly-form', MGQAMeasurementForm.as_view(), name='mg-update-weekly-form'),
    path('api/weekly-qa-result', MGQAResultView.as_view(), name='mg-weekly-qa-result-api')
]
