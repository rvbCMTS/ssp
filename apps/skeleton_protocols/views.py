from django.shortcuts import render
from .models import Protocols
from .filters import ProtocolsFilter

def skeleton_protocols_results(request):
    f = ProtocolsFilter(request.GET, queryset=Protocols.objects.all())
    return render(request,
                  template_name='Protocols.html',
                  context =  {'filter': f})