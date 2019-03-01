from django.conf import settings
from django.shortcuts import render
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
def index(request):
    return render(request, template_name='frontpage/index.html', context=settings.FRONT_PAGE_PARAMETERS)


class Contacts(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        return Response(settings.FRONT_PAGE_PARAMETERS)
