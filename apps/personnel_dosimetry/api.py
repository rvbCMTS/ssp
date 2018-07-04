from rest_framework.generics import ListAPIView

from .serializers import ProfessionSerializer, PersonnelSerializer, AnonymousPersonnelSerializer
from .models import Profession, Personnel


class ProfessionApi(ListAPIView):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class PersonnelApi(ListAPIView):
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer


class AnonymousPersonnelApi(ListAPIView):
    queryset = Personnel.objects.all()
    serializer_class = AnonymousPersonnelSerializer
