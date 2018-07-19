from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from .models import Protocol, Machine, Backup
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
    # if history checkbox is on
    if request.GET.get('history', False) == 'on':
        db_query = Protocol.objects.all()
    else:
        # query to get the latest backup for each machine
        all_machines = Machine.objects.all()
        backup_list = []
        for m in all_machines:
            # for each machine find the latest backup
            backup_list += ([ Backup.objects.all().filter(machine=m).latest() ])
        db_query = Protocol.objects.all().filter(backup__in=backup_list)

    # filter using django_filters
    f = ProtocolsFilter(request.GET, queryset=db_query.order_by('ris_name', 'machine', 'datum'))

    # make data format for Json response
    tt = []
    for obj in f.qs:
        tt.append([obj.ris_name,
                   obj.machine.hospital_name,])
        tt[-1] += [obj.datum.strftime("%Y%m%d"),]
        tt[-1] += [obj.technique,
                   obj.sensitivity,
                   obj.kv,
                   obj.mas,
                   obj.filter_cu,
                   obj.focus,
                   obj.grid,
                   obj.lut,
                   obj.diamond_view,]
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