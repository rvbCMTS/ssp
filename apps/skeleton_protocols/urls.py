from django.urls import path
from .views import skeleton_protocols_results, test_pex_databse


app_name = 'skeleton_protocols'
urlpatterns = [
    path('', skeleton_protocols_results, name='sp-results'),
    path('pex_test', test_pex_databse, name='pex-test'),
]