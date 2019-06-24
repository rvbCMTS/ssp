from django.shortcuts import render
from django.http import JsonResponse
from .models import Protocol, Machine, Backup
from .filter import ProtocolsFilter
from .tools.pex import parse_db
import pandas as pd


def list_exams(request):
    # # query to get the latest backup for each machine
    # backup_list = [Backup.objects.all().filter(machine=m).latest() for m in Machine.objects.all()]
    #
    # # all distinct exams
    # tt = []
    # for e in Protocol.objects.values('exam_name').distinct().filter(backup__in=backup_list):
    #     gg = {}
    #     gg.update({'exam_name': e['exam_name']})
    #
    #     # all protocols and machines for each exam
    #     p_and_m = list(Protocol.objects.values('ris_name', 'machine__hospital_name').filter(backup__in=backup_list, exam_name=e['exam_name']))
    #
    #     # unique dicts in list - machines
    #     h_names = list({v['machine__hospital_name']: v for v in p_and_m}.values())
    #
    #     # sort h_names
    #     h_names = sorted(h_names, key=lambda k: k['machine__hospital_name'])
    #
    #     # build string of h_names
    #     machines_for_exam = ''
    #     for m in h_names:
    #         machines_for_exam += f'{m["machine__hospital_name"]} '
    #
    #     gg.update({'machine': machines_for_exam, 'pk':[]})
    #
    #     # unique list and sorting of ris_names
    #     ris_names = list({v['ris_name']: v for v in p_and_m}.values())
    #     ris_names = sorted(ris_names, key=lambda k: k['ris_name'])
    #
    #     protocols = []
    #     for p in ris_names:
    #
    #         # all primary keys for each protocol
    #         pks = list(Protocol.objects.values('pk').filter(backup__in=backup_list,
    #                                                         exam_name=e['exam_name'],
    #                                                         ris_name=p['ris_name']))
    #         pks = list({v['pk'] for v in pks})
    #
    #         # all machines for each protocol
    #         h_names = list(Protocol.objects.values('machine__hospital_name').filter(backup__in=backup_list,
    #                                                                                 exam_name=e['exam_name'],
    #                                                                                 ris_name=p['ris_name']))
    #
    #         # sort and build string  for h_names
    #         h_names = sorted(h_names, key=lambda k: k['machine__hospital_name'])
    #         machines_for_protocols = ''
    #         for m in h_names:
    #             machines_for_protocols += f'{m["machine__hospital_name"]} '
    #
    #         protocols.append({'pk': pks, 'exam_name': p['ris_name'], 'machine': machines_for_protocols})
    #
    #     gg.update({'children': protocols})
    #
    #     # make Json data format for TreeGrid
    #     tt.append(gg)

    # # query to get the latest backup for each machine
    backup_list = [Backup.objects.all().filter(machine=m).latest() for m in Machine.objects.all()]

    aa = []
    # Get data from database
    df = pd.DataFrame(list(Protocol.objects.filter(backup__in=backup_list).values('ris_name','exam_name','machine__hospital_name','pk')))

    # all distinct exams
    for exam in df.sort_values('exam_name').exam_name.unique():
        # unique machines for this exam, sorted
        machines = df[df['exam_name']==exam].sort_values('machine__hospital_name').machine__hospital_name.unique()

        # build string for machines
        machines_str = ''
        for m in machines:
            machines_str += f'{m} '

        # unique ris_names for this exam, sorted
        ris_names = df[df['exam_name']==exam].sort_values('ris_name').ris_name.unique()

        prot = []
        for p in ris_names:

            # all primary keys for each protocol
            pks = df[(df['ris_name']==p) & (df['exam_name']==exam)].pk.tolist()

            # all machines for each protocol
            machines = df[(df['ris_name']==p) & (df['exam_name']==exam)].sort_values('machine__hospital_name').machine__hospital_name.unique()

            # build string for machines
            machines_protocols_str = ''
            for m in machines:
                machines_protocols_str += f'{m} '

            prot.append({'exam_name': p, 'machine': machines_protocols_str, 'pk': pks})

        aa.append({'exam_name': exam, 'machine': machines_str, 'pk': [], 'children': prot})

    return JsonResponse({'data': aa})

def skeleton_protocols_results(request):
    # primary keys for protocol comparsion
    pks = request.GET.getlist('pk[]')

    if not pks:
        # query to get the latest backup for each machine
        backup_list = [Backup.objects.all().filter(machine=m).latest() for m in Machine.objects.all()]
        db_query = Protocol.objects.all().filter(backup__in=backup_list)
    else:
        db_query = Protocol.objects.all().filter(pk__in=pks)

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



