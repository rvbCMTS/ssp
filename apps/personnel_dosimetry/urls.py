from django.urls import path
from .views import personnel_dosimatery_results, PersonnelDosimetryResultList,\
    api_parse_new_landauer_reports, FilterList, full_body_dosimetry_view, new_personnel_form

app_name = 'personnel_dosimetry'
urlpatterns = [
    path('', personnel_dosimatery_results, name='pd-result'),
    path('fullbody', full_body_dosimetry_view, name='pd-fbd'),
    path('newpersonnel', new_personnel_form, name='pd-np'),
    path('api/results', PersonnelDosimetryResultList.as_view(), name='pd-result-list'),
    path('api/results-filters', FilterList.as_view(), name='pd-result-update-filter-list'),
    path('api/parse-landauer-results', api_parse_new_landauer_reports, name='pd-parse-new-landauer')
]
