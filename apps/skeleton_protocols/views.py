from django.shortcuts import render
from django.http import JsonResponse
from .models import Protocols
from .filter import ProtocolsFilter
from .tools.pex import parse_db

def skeleton_protocols_results(request):
    f = ProtocolsFilter(request.GET)

    return render(request,
                  template_name='skeleton_protocols/Protocols.html',
                  context =  {'filter': f}
                  )

def test_pex_databse(request):
    parse_db('../RontgenProtokoll/mdb_databases/')

    return render (request,
                template_name='skeleton_protocols/Protocols.html',
                    )

def ajax_protocols_results(request):
    f = ProtocolsFilter(request.GET, queryset=Protocols.objects.all().order_by('ris_name'))

    tt = []
    for obj in f.qs:
        tt.append([obj.ris_name,
                   obj.machine.hospital_name,
                   obj.technique,
                   obj.sensitivity,
                   obj.kv,
                   obj.mas,
                   obj.filter_cu,
                   obj.focus,
                   obj.grid,
                   obj.lut,
                   obj.diamond_view,])
        if obj.image_auto_amplification:
            tt[-1] += ['auto',]
        else:
            tt[-1] += [obj.image_amplification_gain,]

        tt[-1] += [f'{obj.edge_filter_kernel_size} | {obj.edge_filter_gain}',
                   f'{obj.harmonization_kernel_size} | {obj.harmonization_gain}',
                   obj.image_auto_amplification,
                   ]

    output = {'data': tt}

    return JsonResponse(output)