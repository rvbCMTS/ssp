from django.shortcuts import render
from django.http import JsonResponse
from .models import Protocol, Machine, Backup, Exam
from .filter import ProtocolsFilter
from .tools.pex import parse_db


def list_exams(request):
    # query to get the latest backup for each machine
    backup_list = []
    for m in Machine.objects.all():
        # for each machine find the latest backup
        backup_list += ([ Backup.objects.all().filter(machine=m).latest() ])

    # all distinct exams
    tt = [];
    for e in Protocol.objects.values('exam_name').distinct().filter(backup__in=backup_list):
        gg = {}
        gg.update({'exam_name': e['exam_name']})

        # all machines for each exam
        machines = ''
        for m in Exam.objects.values('machine__hospital_name').distinct().filter(exam_name=e['exam_name']):
            machines += f'{m["machine__hospital_name"]} '
        gg.update({'machine': machines})

        # all protocols for each exam
        protocols = []
        for p in Exam.objects.values('protocol_name').distinct().filter(exam_name=e['exam_name']):

            # all machines for each protocol
            machines = ''
            for m in Exam.objects.values('machine__hospital_name').distinct().filter(protocol_name=p['protocol_name']):
                machines += f'{m["machine__hospital_name"]} '

            protocols.append({'protocol_name': p['protocol_name'], 'machine': machines})

        gg.update({'children': protocols})

        # make Json data format for TreeGrid
        tt.append(gg)


    return JsonResponse({'data': tt})

def skeleton_protocols_results(request):

    # query to get the latest backup for each machine
    all_machines = Machine.objects.all()
    backup_list = []
    for m in all_machines:
        # for each machine find the latest backup
        backup_list += ([ Backup.objects.all().filter(machine=m).latest() ])
    db_query = Protocol.objects.all().filter(backup__in=backup_list)

    # filter using django_filters
    f = ProtocolsFilter(request.GET, queryset=db_query.order_by('ris_name', 'machine'))

    # make data format for Json response
    tt = []
    for obj in f.qs:
        tt.append([obj.exam_name,])
        tt[-1] += [obj.ris_name,]
        tt[-1] += [obj.machine.hospital_name,]
        tt[-1] += [obj.technique,]
        if obj.technique == '2 pt':
            tt[-1] += ['',]
        else:
            tt[-1] += [obj.sensitivity,]

        tt[-1] += [obj.kv,
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
                   f'{obj.harmonization_kernel_size} | {obj.harmonization_gain}',]
        tt[-1] += [obj.fp_set,]
        if obj.history_flag:
            tt[-1] += [f'<button type="button" class="btn btn-outline-warning btn-sm" onClick="viewHistory({obj.pk})">H</button>',]
        else:
            tt[-1] += ['',]

    return JsonResponse({'data': tt})

def history(request):
    # get primary key
    pk = request.GET.get('pk', None)

    # get protocol entry and associated history
    protocol_entry = Protocol.objects.get(pk=pk)
    previous_versions = protocol_entry.history.all()

    # appending pk protocol and history protocols
    all_protocols = [protocol_entry]
    for obj in previous_versions:
        all_protocols += [obj]


    # make data format for Json response
    tt = []
    for obj in all_protocols:
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
                   f'{obj.harmonization_kernel_size} | {obj.harmonization_gain}',]

    return JsonResponse({'data': tt})


def pex(request):
    return render (request,
                template_name='skeleton_protocols/PexBibliotek.html',
                    )

def skeleton_protocols(request):
    f = ProtocolsFilter(request.GET)

    return render(request,
                  template_name='skeleton_protocols/Protocols.html',
                  context={'filter': f}
                  )

def exams(request):

    return render(request,
                  template_name='skeleton_protocols/Exams.html',
                  )


def pex_read(request):
    parse_db('apps/skeleton_protocols/tools/pex_library')
    return JsonResponse({'data': ''})



