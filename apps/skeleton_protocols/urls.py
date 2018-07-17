from django.urls import path
from .views import skeleton_protocols_results, test_pex_databse, ajax_protocols_results


app_name = 'skeleton_protocols'
urlpatterns = [
    path('', skeleton_protocols_results, name='sp-results'),
    path('pex_test', test_pex_databse, name='pex-test'),
    path('ajax_test', ajax_protocols_results, name='sp-results-list')
]