from django.urls import path
from .views import personnel_dosimatery_results, PersonnelDosimetryAnonymousResultList, PersonnelDosimetryResultList

app_name = 'personnel_dosimetry'
urlpatterns = [
    path('', personnel_dosimatery_results, name='pd-result'),
    path('api/results', PersonnelDosimetryAnonymousResultList.as_view(), name='pd-anonymous-list'),
    path('api/results-non-anon', PersonnelDosimetryResultList.as_view(), name='pd-non-anonymous-list'),
]
