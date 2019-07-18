from django.contrib import messages
from django.shortcuts import render
import json
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import Optional

from .forms import RoomForm
from .models import Room, Department, Clinic, ShieldingClassification
from .serializers import RoomSerializer, DepartmentSerializer, ClinicSerializer, ShieldingClassificationSerializer


def room_list(request):
    q = Department.objects.all().select_related('departmentCategory')
    departments = DepartmentSerializer(q, many=True)
    if departments.data:
        departments = json.dumps(departments.data)
    else:
        departments = []

    q = Clinic.objects.all().select_related('city', 'department', 'department__departmentCategory')
    clinics = ClinicSerializer(q, many=True)
    if clinics.data:
        clinics = JSONRenderer().render(clinics.data)
    else:
        clinics = []

    q = ShieldingClassification.objects.all()
    shieldings_classifications = ShieldingClassificationSerializer(q, many=True)
    if shieldings_classifications.data:
        shieldings_classifications = JSONRenderer().render(shieldings_classifications.data)
    else:
        shieldings_classifications = []
    
    return render(request=request, template_name='radiation_shielding/RoomList.html',
                  context={'department': departments, 'clinic': clinics, 'classification': shieldings_classifications})


def room_details(request, id: int):
    room = Room.objects.get(id=id)
    ser = RoomSerializer(room)
    return render(request=request, context=ser.data, template_name='radiation_shielding/RoomDetail.html')


class RoomListApiView(APIView):
    permission_classes = (permissions.AllowAny,)

    def _get_filters(self, filter_type: str, request):
        if filter_type.lower() == 'department':
            q = Department.objects.all().select_related('departmentCategory')
            return DepartmentSerializer(q, many=True)

        if filter_type.lower() == 'clinic':
            department = request.query_params.get('department')
            if department is not None:
                try:
                    department = int(department)
                except:
                    department = None

            q = Clinic.objects.all().select_related('city', 'department', 'department__departmentCategory')
            if department is not None:
                q = q.filter(department_id__exact=department)

            return ClinicSerializer(q, many=True)

        if filter_type.lower() == 'classification':
            q = ShieldingClassification.objects.all()
            return ShieldingClassificationSerializer(q, many=True)

    def _get_table_data(self, request):
        department_category = request.query_params.get('departmentCategory')
        if department_category is not None:
            try:
                department_category = int(department_category)
            except:
                raise TypeError('Invalid department category data type, must be an integer')

        department = request.query_params.get('department')
        if department is not None:
            try:
                department = int(department)
            except:
                raise TypeError('Invalid department data type, must be an integer')

        clinic = request.query_params.get('clinic')
        if clinic is not None:
            try:
                clinic = int(clinic)
            except:
                raise TypeError('Invalid clinic data type, must be an integer')

        shielding_classification = request.query_params.get('shieldingClassification')
        if shielding_classification is not None:
            try:
                shielding_classification = int(shielding_classification)
            except:
                raise TypeError('Invalid shieldingClassification data type, must be an integer')

        query = Room.objects
        if department_category is not None:
            query = query.filter(clinic__department__departmentCategory_id__exact=department_category)

        if department is not None:
            query = query.filter(clinic__department_id__exact=department)

        if clinic is not None:
            query = query.filter(clinic_id__exact=clinic)

        if shielding_classification is not None:
            query = query.filter(shieldingClassification_id=shielding_classification)

        query = query.all().select_related('clinic', 'clinic__city', 'shieldingClassification')

        return RoomSerializer(query, many=True)

    def get(self, request, format=None):
        filter_type = request.query_params.get('filterType')
        if filter_type is not None:
            ser = self._get_filters(filter_type=filter_type, request=request)
        else:
            try:
                ser = self._get_table_data(request)
            except TypeError as e:
                return Response(data=e, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(data=e, status=status.HTTP_400_BAD_REQUEST)


        if ser.data:
            return Response(data=ser.data, status=status.HTTP_200_OK)
        return Response("Found no valid data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def add_room_form(request, room: Optional[int] = None):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = Room(
                clinic=form.cleaned_data.get('clinic'),
                room=form.cleaned_data.get('room'),
                roomWidth=form.cleaned_data.get('roomWidth'),
                roomLength=form.cleaned_data.get('roomLength'),
                modalityType=form.cleaned_data.get('modalityType'),
                shielding=form.cleaned_data.get('shielding'),
                shieldingClassification=form.cleaned_data.get('shieldingClassification'),
                shieldingClassificationDate=form.cleaned_data.get('shieldingClassificationDate'),
                shieldingClassificationSignature=form.cleaned_data.get('shieldingClassificationSignature'),
                shieldingClassificationComment=form.cleaned_data.get('shieldingClassificationComment'),
                drawing=form.cleaned_data.get('drawing')
            )
            room.save()
            messages.success(request=request,
                             message='Rumsinformationen har sparats')

    context = {'form': form}

    return render(request=request, template_name='radiation_shielding/RoomForm.html', context=context)