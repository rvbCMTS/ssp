from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Max, Q
from .models import Protocol, Machine, Backup
from .filter import ProtocolsFilter
from .tools.pex import parse_db
import pandas as pd


def list_exams(request):
    # # # query to get the latest backup for each machine
    # backup_list = [Backup.objects.all().filter(machine=m).latest() for m in Machine.objects.all()]
    #
    #
    # aa = []
    # # Get data from database
    # df = pd.DataFrame(list(Protocol.objects.filter(backup__in=backup_list).values('ris_name','exam__exam_name','machine__hospital_name','kv','mas','technique','filter_cu','pk','focus','sensitivity','grid')))
    #
    # # all distinct exams
    # for exam in df.sort_values('exam__exam_name').exam__exam_name.unique():
    #     # unique machines for this exam, sorted
    #     machines = df[df['exam__exam_name']==exam].sort_values('machine__hospital_name').machine__hospital_name.unique()
    #
    #     # build string for machines
    #     machines_str = ''
    #     for m in machines:
    #         machines_str += f'<span class="badge badge-secondary">{m}</span>&nbsp;'
    #
    #     # unique protocols for each exam
    #     prot = []
    #     for p in df[df['exam__exam_name']==exam].sort_values('ris_name').ris_name.unique():
    #
    #         # all primary keys for each protocol
    #         pks = df[(df['ris_name']==p) & (df['exam__exam_name']==exam)].pk.tolist()
    #
    #         # all machines for each protocol
    #         machines = df[(df['ris_name']==p) & (df['exam__exam_name']==exam)].sort_values('machine__hospital_name').machine__hospital_name.unique()
    #
    #         # build string for machines
    #         machines_protocols_str = ''
    #         for m in machines:
    #             machines_protocols_str += f'<span class="badge badge-secondary">{m}</span>&nbsp;'
    #
    #         detail = []
    #         for machine in machines:
    #             info = df[(df['ris_name']==p) & (df['exam__exam_name']==exam) & (df['machine__hospital_name']==machine)].values
    #             if info[0][10] == '2 pt':
    #                 detail_str = f'{info[0][4]} kV {info[0][6]} mAs F:{info[0][1]} {info[0][2]} R:{info[0][3]}'
    #             else:
    #                 detail_str = f'{info[0][4]} kV S:{info[0][9]}   F:{info[0][1]} {info[0][2]} R:{info[0][3]}'
    #
    #             pk = df[(df['ris_name']==p) & (df['exam__exam_name']==exam) & (df['machine__hospital_name']==machine)].pk.tolist()
    #             detail.append({'exam_name': f'<span class="badge badge-secondary">{machine}</span>', 'machine': detail_str, 'pk': pk})
    #
    #         prot.append({'exam__exam_name': p, 'machine': machines_protocols_str, 'pk': pks, 'children': detail})
    #
    #     aa.append({'exam__exam_name': exam, 'machine': machines_str, 'pk': [], 'children': prot})
    #
    # return JsonResponse({'data': aa})

    # # query to get the latest backup for each machine
    backup_list = [Backup.objects.all().filter(machine=m).latest() for m in Machine.objects.all()]

    # -- Third level
    # sql-question
    df = pd.DataFrame(list(
        Protocol.objects.filter(backup__in=backup_list).values('ris_name', 'exam_name', 'machine__hospital_name',
                                                               'kv', 'mas', 'technique', 'filter_cu', 'pk', 'focus',
                                                               'sensitivity', 'grid', 'datum')
                                                       .order_by('exam_name', 'ris_name', 'machine__hospital_name')))
    # format machine names and date
    df['date_latest'] = df['datum'].dt.strftime('%Y-%m-%d')
    df['machine__hospital_name'] = df['machine__hospital_name'].apply(lambda x: f'<span class="badge badge-secondary">{x}</span>')

    # detail string
    def details(kv, mas, technique, filter_cu, focus, sensitivity, grid):
        if technique == '2 pt':
            return f'{kv} kV {mas} mAs F:{filter_cu} {focus} R:{grid}'
        else:
            return f'{kv} kV S:{sensitivity} F:{filter_cu} {focus} R:{grid}'
    df['details'] = df.apply (lambda x: details(x['kv'], x['mas'], x['technique'], x['filter_cu'], x['focus'], x['sensitivity'], x['grid']), axis=1)


    # -- Second level
    # Pandas group by to get list of pk and build machine string
    s_pk = df.groupby(['exam_name', 'ris_name'])['pk'].apply(list).reset_index()
    s_machine = df.groupby(['exam_name', 'ris_name'])['machine__hospital_name'].apply(' '.join).reset_index()
    s_date_latest = df.groupby(['exam_name', 'ris_name'])['date_latest'].max().reset_index()



    # -- first level
    # sql-question
    f_df = pd.DataFrame(list(
        Protocol.objects.filter(backup__in=backup_list).values('exam_name', 'machine__hospital_name')
                                                       .annotate(Max('datum'))
                                                       .order_by('exam_name', 'machine__hospital_name')))
    # format machine names
    f_df['machine__hospital_name'] = f_df['machine__hospital_name'].apply(lambda x: f'<span class="badge badge-secondary">{x}</span>')

    # Pandas group by to build machine string and date_latest
    f_machine = f_df.groupby(['exam_name'])['machine__hospital_name'].apply(' '.join).reset_index()
    f_date_latest = df.groupby(['exam_name'])['date_latest'].max().reset_index()


    # Structure for Treegrid
    f_machine['date_latest'] = f_date_latest.date_latest
    main_df = f_machine.rename(columns={'exam_name': 'fc', 'machine__hospital_name': 'sc'})
    main_df['pk'] = ''

    s_machine['date_latest'] = s_date_latest.date_latest
    s_machine['pk'] = s_pk.pk
    second_df = s_machine.rename(columns={'ris_name': 'fc', 'machine__hospital_name': 'sc'})
    df['fc'] = df['machine__hospital_name']
    df['sc'] = df['details']
    second_df['children'] = df.groupby(['exam_name', 'ris_name']).apply(lambda x: x.drop("exam_name", 1).to_dict('records')).tolist()
    main_df['children'] = second_df.groupby(['exam_name']).apply(lambda x: x.drop("exam_name", 1).to_dict('records')).tolist()




    # # all distinct exams
    # tt = []
    # for e in Protocol.objects.filter(backup__in=backup_list).values('exam__exam_name').distinct():
    #
    #     # unique machines for this exam, sorted
    #     machines = Protocol.objects.values('machine__hospital_name').distinct().order_by('machine__hospital_name').filter(exam__exam_name=e['exam__exam_name'], backup__in=backup_list)
    #
    #     # build string for machines
    #     machines_str = ''
    #     for m in machines:
    #         machines_str += f'<span class="badge badge-secondary">{m["machine__hospital_name"]}</span>&nbsp;'
    #
    #
    #     # unique protocols for each exam
    #     prot = []
    #     for p in Protocol.objects.values('ris_name').distinct().order_by('ris_name').filter(exam__exam_name=e['exam__exam_name'], backup__in=backup_list):
    #
    #         # all unique machines for each protocol, sorted
    #         machines_protocols = Protocol.objects.values('machine__hospital_name').order_by('machine__hospital_name').\
    #                             filter(exam__exam_name=e['exam__exam_name'], backup__in=backup_list, ris_name=p['ris_name'])
    #
    #         # build string for machines
    #         machines_protocols_str = ''
    #         for m in machines_protocols:
    #             machines_protocols_str += f'<span class="badge badge-secondary">{m["machine__hospital_name"]}</span>&nbsp;'
    #
    #         # all pk for each protocol, sorted
    #         pks = list(Protocol.objects.values('pk').order_by('ris_name').\
    #                             filter(exam__exam_name=e['exam__exam_name'], backup__in=backup_list, ris_name=p['ris_name']))
    #         pks = list({v['pk'] for v in pks})
    #
    #         prot.append({'exam__exam_name': p['ris_name'], 'machine': machines_protocols_str, 'pk': pks})
    #
    #     tt.append({'exam__exam_name': e['exam__exam_name'], 'machine': machines_str, 'pk': [], 'children': prot})

    return JsonResponse({'data': main_df.to_dict('records')})

def skeleton_protocols_results(request):
    # primary keys for protocol comparsion
    pks = request.GET.getlist('pk[]')

    # Protocol question
    q_prot = Protocol.objects.values('pk', 'exam_name','ris_name', 'machine__hospital_name','technique',
                                     'sensitivity', 'kv', 'mas', 'filter_cu', 'focus', 'grid', 'lut', 'diamond_view',
                                     'image_auto_amplification', 'image_amplification_gain', 'edge_filter_kernel_size',
                                     'edge_filter_gain', 'harmonization_kernel_size', 'harmonization_gain', 'fp_set',
                                     'history','datum')


    if not pks:
        # query to get the latest backup for each machine
        backup_list = [Backup.objects.all().filter(machine=m).latest() for m in Machine.objects.all()]
        db_query = q_prot.filter(backup__in=backup_list)
    else:
        db_query = q_prot.filter(pk__in=pks)

    # filter using django_filters
    f = ProtocolsFilter(request.GET, queryset=db_query)

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
        if obj["history"] is not None:
            obj.update({'history': f'<button type="button" class="btn btn-outline-warning btn-sm" onClick="viewHistory({obj["pk"]})">H</button>'})
        else:
            obj.update({'history': ''})

        # Remove sensitivity for 2pt
        if obj["technique"]=='2 pt':
            obj["sensitivity"]=''

        # format date
        obj["datum"] = obj["datum"].strftime("%Y-%m-%d")

        # format machine
        obj["machine__hospital_name"] = f'<span class="badge badge-secondary">{obj["machine__hospital_name"]}</span>'


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
               'datum':p.datum.strftime("%Y-%m-%d")
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

        # format machine
        obj["machine__hospital_name"] = f'<span class="badge badge-secondary">{obj["machine__hospital_name"]}</span>'

        tt.append(obj)

    return JsonResponse({'data': tt})

def backup(request):

    # List of latest backups
    backup_list = [Backup.objects.all().values('pk').filter(machine=m).latest() for m in Machine.objects.all()]
    pks = [b['pk'] for b in backup_list]
    # lab and date
    backup_data = list(Backup.objects.values('machine__hospital_name', 'datum').filter(pk__in=pks).order_by('machine__hospital_name'))

    for obj in backup_data:
        # format date
        obj["datum"] = obj["datum"].strftime("%Y-%m-%d %H:%M:%S")

        # format machine
        obj["machine__hospital_name"] = f'<span class="badge badge-secondary">{obj["machine__hospital_name"]}</span>'

    return JsonResponse({'data': backup_data})



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



