from django.urls import path
from .views import index, Contacts

app_name = 'home'
urlpatterns = [
    path('', index, name='home'),
    path('api/front-page-contacts', Contacts.as_view(), name='front-page-contacts')
]
