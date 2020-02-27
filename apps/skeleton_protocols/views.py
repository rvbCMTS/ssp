from django.shortcuts import render
from django.http import JsonResponse
from .models import Protocol, Machine, Backup
from .filter import ProtocolsFilter
from .tools.pex import parse_db
import pandas as pd


def list_exams(request):
    # # query to get the latest backup for each machine
    backup_list = [Backup.objects.all().filter(machine=m).latest() for m in Machine.objects.all()]

    aa = []
    # Get data from database
    df = pd.DataFrame(list(Protocol.objects.filter(backup__in=backup_list).values('ris_name','exam__exam_name','machine__hospital_name','kv','mas','technique','filter_cu','pk','focus','sensitivity','grid')))

    # all distinct exams
    for exam in df.sort_values('exam__exam_name').exam__exam_name.unique():
        # unique machines for this exam, sorted
        machines = df[df['exam__exam_name']==exam].sort_values('machine__hospital_name').machine__hospital_name.unique()

        # build string for machines
        machines_str = ''
        for m in machines:
            machines_str += f'<span class="badge badge-secondary">{m}</span>&nbsp;'

        # unique protocols for each exam
        prot = []
        for p in df[df['exam__exam_name']==exam].sort_values('ris_name').ris_name.unique():

            # all primary keys for each protocol
            pks = df[(df['ris_name']==p) & (df['exam__exam_name']==exam)].pk.tolist()

            # all machines for each protocol
            machines = df[(df['ris_name']==p) & (df['exam__exam_name']==exam)].sort_values('machine__hospital_name').machine__hospital_name.unique()

            # build string for machines
            machines_protocols_str = ''
            for m in machines:
                machines_protocols_str += f'<span class="badge badge-secondary">{m}</span>&nbsp;'

            detail = []
            for machine in machines:
                info = df[(df['ris_name']==p) & (df['exam__exam_name']==exam) & (df['machine__hospital_name']==machine)].values
                if info[0][10] == '2 pt':
                    detail_str = f'{info[0][4]} kV {info[0][6]} mAs F:{info[0][1]} {info[0][2]} R:{info[0][3]}'
                else:
                    detail_str = f'{info[0][4]} kV S:{info[0][9]}   F:{info[0][1]} {info[0][2]} R:{info[0][3]}'

                pk = df[(df['ris_name']==p) & (df['exam__exam_name']==exam) & (df['machine__hospital_name']==machine)].pk.tolist()
                detail.append({'exam_name': f'<span class="badge badge-secondary">{machine}</span>', 'machine': detail_str, 'pk': pk})

            prot.append({'exam__exam_name': p, 'machine': machines_protocols_str, 'pk': pks, 'children': detail})

        aa.append({'exam__exam_name': exam, 'machine': machines_str, 'pk': [], 'children': prot})

    return JsonResponse({'data': aa})

    # # # query to get the latest backup for each machine
    # backup_list = [Backup.objects.all().filter(machine=m).latest() for m in Machine.objects.all()]
    #
    # # all distinct exams
    # tt = []
    # for exam in Protocol.objects.filter(backup__in=backup_list).values('exam_name').distinct():
    #
    #     # unique machines for this exam, sorted
    #     machines = Protocol.objects.values('machine__hospital_name').distinct().order_by('machine__hospital_name').filter(exam_name=exam['exam_name'], backup__in=backup_list)
    #
    #     # build string for machines
    #     machines_str = ''
    #     for m in machines:
    #         machines_str += f'{m["machine__hospital_name"]} '
    #
    #
    #     prot = []
    #     for protocol in Protocol.objects.values('ris_name').distinct().order_by('ris_name').filter(exam_name=exam['exam_name'], backup__in=backup_list):
    #
    #         # all unique machines for each protocol, sorted
    #         machines_protocols = Protocol.objects.values('machine__hospital_name').order_by('machine__hospital_name').\
    #                             filter(exam_name=exam['exam_name'], backup__in=backup_list, ris_name=protocol['ris_name'])
    #
    #         # build string for machines
    #         machines_protocols_str = ''
    #         for m in machines_protocols:
    #             machines_protocols_str += f'{m["machine__hospital_name"]} '
    #
    #         # all pk for each protocol, sorted
    #         pks = list(Protocol.objects.values('pk').order_by('ris_name').\
    #                             filter(exam_name=exam['exam_name'], backup__in=backup_list, ris_name=protocol['ris_name']))
    #         pks = list({v['pk'] for v in pks})
    #
    #         prot.append({'exam_name': protocol['ris_name'], 'machine': machines_protocols_str, 'pk': pks})
    #
    #     tt.append({'exam_name': exam['exam_name'], 'machine': machines_str, 'pk': [], 'children': prot})
    #
    # return JsonResponse({'data': tt})

def skeleton_protocols_results(request):
    # primary keys for protocol comparsion
    pks = request.GET.getlist('pk[]')

    # Protocol question
    q_prot = Protocol.objects.values('pk', 'exam__exam_name', 'ris_name', 'machine__hospital_name','technique',
                                     'sensitivity', 'kv', 'mas', 'filter_cu', 'focus', 'grid', 'lut', 'diamond_view',
                                     'image_auto_amplification', 'image_amplification_gain', 'edge_filter_kernel_size',
                                     'edge_filter_gain', 'harmonization_kernel_size', 'harmonization_gain', 'fp_set',
                                     'history_flag')

    if not pks:
        # query to get the latest backup for each machine
        backup_list = [Backup.objects.all().filter(machine=m).latest() for m in Machine.objects.all()]
        db_query = q_prot.filter(backup__in=backup_list)
    else:
        db_query = q_prot.filter(pk__in=pks)

    # filter using django_filters
    f = ProtocolsFilter(request.GET, queryset=db_query.order_by('ris_name', 'machine'))

    # make data format for Json response
    tt = []
    for obj in f.qs:
        # combined strings for edge and harmonization
        obj.update({'edge': f'{obj["edge_filter_kernel_size"]} | {obj["edge_filter_gain"]}',
                  'harm': f'{obj["harmonization_kernel_size"]} | {obj["harmonization_gain"]}'})

        # image amplification
        if obj["image_auto_amplification"]:
            obj.update({'image_amp': 'A'})
        else:
            obj.update({'image_amp': obj["image_amplification_gain"]})

        # history button
        if obj["history_flag"]:
            obj.update({'history': f'<button type="button" class="btn btn-outline-warning btn-sm" onClick="viewHistory({obj["pk"]})">H</button>'})
        else:
            obj.update({'history': ''})

        # Remove sensitivity for 2pt
        if obj["technique"]=='2 pt':
            obj["sensitivity"]=''

        tt.append(obj)

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
    for p in all_protocols:
        # create dict
        obj = {'ris_name':p.ris_name,
               'machine__hospital_name': p.machine.hospital_name,
               'kv': p.kv,
               'sensitivity': p.sensitivity,
               'mas':p.mas,
               'filter_cu':p.filter_cu,
               'focus':p.focus,
               'grid':p.grid,
               'fp_set':p.fp_set,
               'lut':p.lut,
               'diamond_view':p.diamond_view,
               'datum':p.datum.strftime("%Y%m%d")
               }

        # combined strings for edge and harmonization
        obj.update({'edge': f'{p.edge_filter_kernel_size} | {p.edge_filter_gain}',
                  'harm': f'{p.harmonization_kernel_size} | {p.harmonization_gain}'})

        # image amplification
        if p.image_auto_amplification:
            obj.update({'image_amp': 'A'})
        else:
            obj.update({'image_amp': p.image_amplification_gain})

        # Remove sensitivity for 2pt
        if p.technique=='2 pt':
            obj["sensitivity"]=''

        tt.append(obj)

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



