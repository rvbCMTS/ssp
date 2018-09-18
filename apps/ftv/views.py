from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .forms import FtvOP300QAForm
from .models import Machine, QaTestInstructions, OP300TestQA, OP300CBCTTest, OP300PanTest, OP300CefTest
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


def op300_test_form(request):
    if request.method == 'POST':
        form = FtvOP300QAForm(request.POST)
        cbct_form = None
        pan_form = None
        cef_form = None

        if form.is_valid() and request.POST.get('modality_change', None) is not None and int(request.POST.get('modality_change')) == 0:
            machine_type: str = form.cleaned_data['modality'].machine_type.machine_type

            measurement = OP300TestQA(
                machine=form.cleaned_data['modality'],
                qa_date=form.cleaned_data['qa_date'],
                signature=form.cleaned_data['signature'],
                comment=form.cleaned_data['comment']
            )
            measurement.save()

            if 'CBCT' in machine_type.upper():
                cbct_measurement = OP300CBCTTest(
                    test=measurement,
                    calibration_run=form.cleaned_data['calibration_run'],
                    cbct_geom=form.cleaned_data['cbct_geom'],
                    cbct_geom_ctq=form.cleaned_data['cbct_geom_ctq'],
                    cbct_geom_scan_diff=form.cleaned_data['cbct_geom_scan_diff'],
                    cbct_geom_x_offset=form.cleaned_data['cbct_geom_x_offset'],
                    cbct_geom_y_offset=form.cleaned_data['cbct_geom_y_offset'],
                    cbct_geom_n_offset=form.cleaned_data['cbct_geom_n_offset'],
                    cbct_geom_j_offset=form.cleaned_data['cbct_geom_j_offset'],
                    cbct_pix=form.cleaned_data['cbct_pix'],
                    cbct_pix_ctq=form.cleaned_data['cbct_pix_ctq'],
                    cbct_pix_signal_level=form.cleaned_data['cbct_pix_signal_level'],
                    cbct_pix_dark_level=form.cleaned_data['cbct_pix_dark_level'],
                    cbct_qc=form.cleaned_data['cbct_qc'],
                    cbct_qc_pmma_max_value=form.cleaned_data['cbct_qc_pmma_max_value'],
                    cbct_qc_pmma_min_value=form.cleaned_data['cbct_qc_pmma_min_value'],
                    cbct_qc_pmma_std_dev=form.cleaned_data['cbct_qc_pmma_std_dev'],
                    cbct_qc_pfte=form.cleaned_data['cbct_qc_pfte'],
                    cbct_qc_ptfe_std_dev=form.cleaned_data['cbct_qc_ptfe_std_dev'],
                    cbct_qc_air=form.cleaned_data['cbct_qc_air'],
                    cbct_qc_air_std_dev=form.cleaned_data['cbct_qc_air_std_dev']
                )
                cbct_measurement.save()
            if 'PAN' in machine_type.upper():
                pan_measurement = OP300PanTest(
                    test=measurement,
                    calibration_run=form.cleaned_data['calibration_run'],
                    pan_geom=form.cleaned_data['pan_geom'],
                    pan_geom_x_offset=form.cleaned_data['pan_geom_x_offset'],
                    pan_geom_y_offset=form.cleaned_data['pan_geom_y_offset'],
                    pan_geom_n_offset=form.cleaned_data['pan_geom_n_offset'],
                    pan_geom_j_offset=form.cleaned_data['pan_geom_j_offset'],
                    pan_pix=form.cleaned_data['pan_pix'],
                    pan_pix_ctq=form.cleaned_data['pan_pix_ctq'],
                    pan_pix_signal_level=form.cleaned_data['pan_pix_signal_level'],
                    pan_pix_dark_level=form.cleaned_data['pan_pix_dark_level'],
                    pan_qc=form.cleaned_data['pan_qc'],
                    pan_qc_homogeneous=form.cleaned_data['pan_qc_homogeneous'],
                    pan_qc_high_contrast=form.cleaned_data['pan_qc_high_contrast'],
                    pan_qc_low_contrast=form.cleaned_data['pan_qc_low_contrast'],
                    pan_qc_round_ball=form.cleaned_data['pan_qc_round_ball'],
                    pan_qc_distance_white_rods_ball=form.cleaned_data['pan_qc_distance_white_rods_ball']
                )
                pan_measurement.save()
            if 'CEF' in machine_type.upper():
                cef_measurement = OP300PanTest(
                    test=measurement,
                    calibration_run=form.cleaned_data['calibration_run'],
                    cef_pix=form.cleaned_data['cef_pix'],
                    cef_qc=form.cleaned_data['cef_qc'],
                    cef_qc_homogeneous=form.cleaned_data['cef_qc_homogeneous'],
                    cef_qc_low_contrast=form.cleaned_data['cef_qc_low_contrast'],
                    cef_qc_round_ball=form.cleaned_data['cef_qc_round_ball']
                )
                cef_measurement.save()

        elif request.POST.get('modality', None) is not None and request.POST.get('modality_change', None):
            # Update the form to one adapted to the selected modality
            modality = request.POST.get('modality', None)
            modality_change = request.POST.get('modality_change', None)
            try:
                modality = int(modality)
                modality_change = int(modality_change)
            except:
                modality = None
                modality_change = None

            if modality is not None and modality_change is not None and modality_change == 1:
                modality = Machine.objects.get(id=modality)
                form = FtvOP300QAForm(initial={'modality': modality.id})

                cbct = False
                pan = False
                cef = False
                machine_type = modality.machine_type.machine_type
                if 'CBCT' in machine_type.upper():
                    cbct = True
                if 'PAN' in machine_type.upper():
                    pan = True
                if 'CEF' in machine_type.upper():
                    cef = True

                return render(request=request, template_name='ftv/op300_form.html',
                              context={'form': form, 'show_form': True,
                                       'cbct': cbct, 'pan': pan, 'cef': cef}
                              )

    form = FtvOP300QAForm()

    return render(request=request, template_name='ftv/op300_form.html', context={'form': form})



