"""ssp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from rest_framework import routers
from .serializers import UserViewSet


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include('apps.frontpage.urls', namespace='home')),
    path('persondosimetri/', include('apps.personnel_dosimetry.urls', namespace='pd')),
    path('genomlysning/', include('apps.fluoro_times.urls', namespace='gls')),
    path('mammo/', include('apps.mammography.urls', namespace='mg')),
    path('skelettprotokoll/', include('apps.skeleton_protocols.urls', namespace='sp')),
    path('radpharmprod/', include('apps.radpharmprod.urls', namespace='radpharmprod')),
    path('radshielding/', include('apps.radiation_shielding.urls', namespace='radiation_shielding')),
    path('api/routers', include(router.urls)),
    path('admin/', admin.site.urls, name='admin'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
