from django.urls import path
from .views import AcrResultView


app_name = 'mri'
urlpatterns = [
    path('api/result/', AcrResultView.as_view(), name='acr_result_api')
]
