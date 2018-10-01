from django.urls import path
from .views import skeleton_protocols_results, ajax_protocols_results, pex, pex_read, history


app_name = 'skeleton_protocols'
urlpatterns = [
    path('', skeleton_protocols_results, name='sp-results'),
    path('ajax_test', ajax_protocols_results, name='sp-results-list'),
    path('pex', pex, name='sp-pex'),
    path('pex_read', pex_read, name='sp-pex-read'),
    path('history', history, name='sp-history')
]


