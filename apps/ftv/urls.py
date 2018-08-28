from django.urls import path
from .views import list_ftv_machines, MachineInfoList


app_name = 'ftv'
urlpatterns = [
    path('', list_ftv_machines, name='machines'),
    path('api/machine_info_list/', MachineInfoList.as_view(), name='machine_info_list')
]
