from django.urls import path
from .views import InputView

app_name = "mri"
urlpatterns = [
    path('booktitle', InputView.as_view(), name="book-title")
]


