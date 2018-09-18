from django.urls import path
from .views import list_ftv_machines, MachineInfoList, op300_test_form


app_name = 'ftv'
urlpatterns = [
    path('', list_ftv_machines, name='machines'),
    path('op300_test', op300_test_form, name='op300_form'),
    path('api/machine_info_list/', MachineInfoList.as_view(), name='machine_info_list')
]
