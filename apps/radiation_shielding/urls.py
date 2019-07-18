from django.urls import path
from .views import (room_list, RoomListApiView, room_details, add_room_form)


app_name = 'radiation_shielding'
urlpatterns = [
    path('', room_list, name='roomlist'),
    path('room/<int:id>', room_details, name='roomdetail'),
    path('api/room-list', RoomListApiView.as_view(), name='roomlistapi')
]
