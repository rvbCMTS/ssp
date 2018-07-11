from django.urls import path
from .views import personnel_dosimatery_results, PersonnelDosimetryResultList,\
    api_parse_new_landauer_reports, FilterList

app_name = 'personnel_dosimetry'
urlpatterns = [
    path('', personnel_dosimatery_results, name='pd-result'),
    path('api/results', PersonnelDosimetryResultList.as_view(), name='pd-result-list'),
    path('api/results-filters', FilterList.as_view(), name='pd-result-update-filter-list'),
    path('api/parse-landauer-results', api_parse_new_landauer_reports, name='pd-parse-new-landauer')
]
