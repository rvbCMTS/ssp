from django.shortcuts import render
from .models import Protocols
from .filter import ProtocolsFilter

def skeleton_protocols_results(request):
    f = ProtocolsFilter(request.GET, queryset=Protocols.objects.all())
    return render(request,
                  template_name='skeleton_protocols/Protocols.html',
                  context =  {'filter': f})