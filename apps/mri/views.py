from django.shortcuts import render
from django.utils import timezone
import json
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import Optional

from .models import (AcrResult, ManufacturerModelName, ReportedMachine)
from .serializers import AcrResultSerializer, AcrResultInsertSerializer, ManufacturerModelNameSerializer


DEFAULT_TIME_LIMIT = 10000  # days


def acr_results(request):
    filter_data = _get_acr_filters(time_limit=DEFAULT_TIME_LIMIT)
    return render(request=request, template_name='mri/AcrResult.html',
                  context={'filterData': json.dumps(filter_data)})


def _get_acr_filters(time_limit: Optional[int] = None, modality: Optional[int] = None):
    if not time_limit:
        time_limit = DEFAULT_TIME_LIMIT
    first_date = timezone.now() - timezone.timedelta(days=time_limit)

    query = AcrResult.objects.filter(acquisition_time__gte=first_date)

    if modality:
        query = query.filter(reported_machine__machine_id__exact=modality)

    query = query.values(
        'reported_machine__machine_id', 'reported_machine__machine__display_name',
        'receive_coil_name',
        'series_description'
    ).distinct()

    output = {}
    if len(query) < 1:
        return output

    for row in query:
        machine_id = str(row['reported_machine__machine_id'])
        if machine_id not in output.keys():
            output[machine_id] = {
                'displayName': row['reported_machine__machine__display_name'],
                'coilsAndSequences': [],
            }

        output[machine_id]['coilsAndSequences'].append(
            {
                'coil': row['receive_coil_name'],
                'sequence': row['series_description']
            }
        )

    return output


def _get_acr_result(time_limit: Optional[int] = None, modality: Optional[int] = None,
                    coil: Optional[str] = None, sequence: Optional[str] = None):
    if not time_limit or time_limit < 0:
        time_limit = DEFAULT_TIME_LIMIT

    first_date = timezone.now() - timezone.timedelta(days=time_limit)
    query = AcrResult.objects.filter(acquisition_time__gte=first_date)

    if modality and isinstance(modality, int):
        query = query.filter(reported_machine__machine_id__exact=int)

    if coil:
        query = query.filter(receive_coil_name__exact=coil)

    if sequence:
        query = query.filter(series_description__exact=sequence)

    query = query.prefetch_related(
        'reported_machine', 'reported_machine__machine_model', 'reported_machine__machine'
    ).all()
    ser = AcrResultSerializer(query, many=True)
    if ser.data:
        return True, ser.data

    return False, None


class AcrUpdateFilterView(APIView):

    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        time_limit = request.query_params.get('timeLimit');
        try:
            time_limit = int(time_limit)
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_get_acr_filters(time_limit=time_limit), status=status.HTTP_200_OK)



class AcrResultView(APIView):

    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        time_limit = request.query_params.get('timeLimit')
        try:
            time_limit = int(time_limit)
        except:
            time_limit = DEFAULT_TIME_LIMIT

        machine = request.query_params.get('machine')
        try:
            machine = int(machine)
        except:
            machine = None

        try:
            first_date = timezone.now() - timezone.timedelta(days=time_limit)
            query = AcrResult.objects.filter(acquisition_time__gte=first_date)

            if machine:
                query = query.filter(reported_machine__machine_id__exact=machine)

            query = query.prefetch_related(
                'reported_machine', 'reported_machine__machine_model', 'reported_machine__machine'
            ).all()
            ser = AcrResultSerializer(query, many=True)
            if ser.data:
                return Response(ser.data, status=status.HTTP_200_OK)
            return Response(ser.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        try:
            data = request.data

            reported_machine = data.pop('reported_machine')
            if not reported_machine or any([key not in ['device_serial_number', 'machine_model'] for key in reported_machine]):
                Response({}, status=status.HTTP_400_BAD_REQUEST)

            machine_model = reported_machine.get('machine_model')
            if not machine_model or any([key not in ['name', 'manufacturer'] for key in machine_model.keys()]):
                Response({}, status=status.HTTP_400_BAD_REQUEST)

            # Check if machine model exist
            machine_model_object = ManufacturerModelName.objects.filter(
                name=machine_model.get('name'),
                manufacturer=machine_model.get('manufacturer')).first()

            if not machine_model_object:
                machine_model_object = ManufacturerModelName(
                    name=machine_model.get('name'),
                    manufacturer=machine_model.get('manufacturer')
                )
                machine_model_object.save()

            # Check if reported machine exist
            reported_machine_object = ReportedMachine.objects.filter(
                device_serial_number=reported_machine.get('device_serial_number'),
                machine_model_id=machine_model_object.id
            ).first()

            if not reported_machine_object:
                reported_machine_object = ReportedMachine(
                    device_serial_number=reported_machine.get('device_serial_number'),
                    machine_model_id=machine_model_object.id
                )
                reported_machine_object.save()

            acr_obj = AcrResult.objects.filter(
                patient_id=data.get('patient_id'),
                series_instance_uid=data.get('series_instance_uid'),
                study_instance_uid=data.get('study_instance_uid')
            ).first()

            if acr_obj:
                Response({}, status=status.HTTP_400_BAD_REQUEST)

            acr_obj = AcrResult(
                reported_machine_id=reported_machine_object.id,
                patient_id=data.get('patient_id'),
                patient_weight=data.get('patient_weight'),
                patient_position=data.get('patient_position'),
                folder=data.get('folder'),
                acquisition_time=data.get('acquisition_time'),
                study_time=data.get('study_time'),
                protocol_name=data.get('protocol_name'),
                series_description=data.get('series_description'),
                series_instance_uid=data.get('series_instance_uid'),
                study_instance_uid=data.get('study_instance_uid'),
                study_id=data.get('study_id'),
                operator=data.get('operator'),
                operator_name=data.get('operator_name'),
                software_version=data.get('software_version'),
                receive_coil_name=data.get('receive_coil_name'),
                echo_time=data.get('echo_time'),
                repetition_time=data.get('repetition_time'),
                actual_receive_gain_analog=data.get('actual_receive_gain_analog'),
                actual_receive_gain_digital=data.get('actual_receive_gain_digital'),
                auto_prescan_gain_digital=data.get('auto_prescan_gain_digital'),
                auto_prescan_center_frequency=data.get('auto_prescan_center_frequency'),
                auto_prescan_transmit_gain=data.get('auto_prescan_transmit_gain'),
                auto_prescan_analog_receiver_gain=data.get('auto_prescan_analog_receiver_gain'),
                auto_prescan_digital_receiver_gain=data.get('auto_prescan_digital_receiver_gain'),
                transmitting_coil_type=data.get('transmitting_coil_type'),
                surface_coil_type=data.get('surface_coil_type'),
                prescan_type=data.get('prescan_type'),
                transmit_gain=data.get('transmit_gain'),
                db_dt_peak_rate_of_change_of_gradient_field=data.get('db_dt_peak_rate_of_change_of_gradient_field'),
                ge_coil_name=data.get('ge_coil_name'),
                image_frequency=data.get('image_frequency'),
                pixel_bandwidth=data.get('pixel_bandwidth'),
                image_position=data.get('image_position'),
                rotation=data.get('rotation'),
                center_x=data.get('center_x'),
                center_y=data.get('center_y'),
                ghosting_ratio_slice5=data.get('ghosting_ratio_slice5'),
                ghosting_ratio_slice5_std=data.get('ghosting_ratio_slice5_std'),
                max_roi_mean=data.get('max_roi_mean'),
                min_roi_mean=data.get('min_roi_mean'),
                percent_uniformity_integral=data.get('percent_uniformity_integral'),
                ghosting_ratio=data.get('ghosting_ratio'),
                noise=data.get('noise'),
                slice_position_accuracy_slice1=data.get('slice_position_accuracy_slice1'),
                slice_position_accuracy_slice11=data.get('slice_position_accuracy_slice11'),
                slice_thickness=data.get('slice_thickness'),
                diameter_x_slice1=data.get('diameter_x_slice1'),
                diameter_y_slice1=data.get('diameter_y_slice1'),
                diameter_diag1_slice1=data.get('diameter_diag1_slice1'),
                diameter_diag2_slice1=data.get('diameter_diag2_slice1'),
                diameter_x_slice5=data.get('diameter_x_slice5'),
                diameter_y_slice5=data.get('diameter_y_slice5'),
                diameter_diag1_slice5=data.get('diameter_diag1_slice5'),
                diameter_diag2_slice5=data.get('diameter_diag2_slice5'),
                ul_1_score=data.get('ul_1_score'),
                lr_1_score=data.get('lr_1_score'),
                ul_2_score=data.get('ul_2_score'),
                lr_2_score=data.get('lr_2_score'),
                ul_3_score=data.get('ul_3_score'),
                lr_3_score=data.get('lr_3_score')
            )
            acr_obj.save()
            return Response({acr_obj.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
