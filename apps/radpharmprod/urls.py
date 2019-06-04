from django.urls import path
from .views import radpharmstat, api_import_production_data, api_get_statistics


app_name = 'radpharmprod'
urlpatterns = [
    path('', radpharmstat, name='radpharmpro-stat'),
    path('api/get_statistics', api_get_statistics, name='radpharmprod-get-statistics'),
    path('api/import-production-data', api_import_production_data, name='radpharmprod-import-data')
]
