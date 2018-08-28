from django.shortcuts import render
from rest_framework import permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Machine
from .serializers import MachineSerializer


def list_ftv_machines(request):
    return render(request=request, template_name='ftv/machine_list.html')


class MachineInfoList(generics.ListAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = MachineSerializer

    def get_queryset(self):
        active = self.request.query_params.get('active', 1)
        if isinstance(active, str):
            active = int(active)

        machines = Machine.objects

        # Filter on in_use. If active==2 all machines, if active==1 only active machine if active==0 onlu inactive
        # machines
        if active < 2:
            if active == 1:
                machines.filter(in_use=True)
            else:
                machines.filter(in_use=False)

        return machines
