from datetime import datetime as dt
from django.conf import settings
from django.db.models.functions import TruncYear
from django.shortcuts import render
from django.http import Http404
from rest_framework import status, authentication, permissions
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .functions import import_personnel_dosimetry_report
from .models import Clinic, Profession, Personnel, DosimeterPlacement, VendorDosimeterPlacement, Result
from .permissions import IsPersonnelDosimetryAdministrator
from .serializers import ProfessionSerializer, AnonymousPersonnelSerializer, PersonnelSerializer,\
    DosimeterPlacementSerializer, VendorDosimeterPlacementSerializer, PersonnelDosimetryResultSerializer


def personnel_dosimatery_results(request):
    # Get a reversed list of years with dosimetry data
    years = Result.objects.annotate(year=TruncYear('measurement_period_center')).order_by('-year').values('year')

    # Get a list of the clinics
    clinics = Clinic.objects.order_by('display_clinic', 'clinic').all()
    clinics = [{'id': obj.pk, 'name': obj.display_clinic} for obj in clinics]

    # Get a list of professions
    profession = Profession.objects.order_by('profession').all()
    profession = [{'id': obj.pk, 'name': obj.profession} for obj in profession]
    
    return render(request=request, template_name='personnel_dosimetry/DosimetryResults.html',
                  context={
                      'filter_years': years,
                      'clinic': clinics,
                      'personnel_category': profession
                  })


def api_parse_new_landauer_reports(request):
    test = import_personnel_dosimetry_report(
        vendor='Landauer',
        input_file_directory=settings.PERSONNEL_DOSIMETRY_DIRS['Landauer']['incoming'],
        output_file_directory=settings.PERSONNEL_DOSIMETRY_DIRS['Landauer']['outgoing']
    )

    return Response(test)


class PersonnelDosimetryResultList(APIView):
    """
    List all personnel dosimetry results
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsPersonnelDosimetryAdministrator, permissions.IsAdminUser,)

    def get(self, request, format=None):
        results = Result.objects.all()
        serializer = PersonnelDosimetryResultSerializer(results, many=True)
        return Response(serializer.data)


class PersonnelDosimetryAnonymousResultList(APIView):
    """
    List all personnel dosimetry results
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        result = Result.objects.all()
        serializer = PersonnelDosimetryResultSerializer(result, many=True)
        return Response(serializer.data)
