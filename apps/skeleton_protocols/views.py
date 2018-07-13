from django.shortcuts import render
from .models import Protocols
from .filter import ProtocolsFilter
from .tools.pex import parse_db

def skeleton_protocols_results(request):
    f = ProtocolsFilter(request.GET, queryset=Protocols.objects.all().order_by('ris_name'))

    return render(request,
                  template_name='skeleton_protocols/Protocols.html',
                  context =  {'filter': f}
                  )

def test_pex_databse(request):
    parse_db('../RontgenProtokoll/mdb_databases/')

    return render (request,
                template_name='skeleton_protocols/Protocols.html',
                    )
