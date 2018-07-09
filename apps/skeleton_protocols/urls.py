from django.urls import path
from .views import skeleton_protocols_results


app_name = 'skeleton_protocols'
urlpatterns = [
    path('', skeleton_protocols_results, name='sp-results'),
]