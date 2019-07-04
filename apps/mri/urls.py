from django.urls import path
from .views import AcrResultView, acr_results


app_name = 'mri'
urlpatterns = [
    path('', acr_results, name='acr_result'),
    path('api/updateacrfilterlist/', acr_results, name='mri-update-filter-list'),
    path('api/result/', AcrResultView.as_view(), name='acr_result_api'),
]
