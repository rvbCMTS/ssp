from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, Http404
from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import MammographyWeeklyQAForm, ROIForm
from .models import Modality, Reference, Measurement, RoiValue
from .serializers import ModalityMeasurementSerializer, ModalityReferenceSerializer


def mgqa_measurement_form(request):
    if request.method == 'POST':
        form = MammographyWeeklyQAForm(request.POST)
        if form.is_valid():
            roi_form = ROIForm(request.POST, rois=form.cleaned_data['modality'].number_of_rois)
            if roi_form.is_valid():
                # Go through the measured data and save it to the database
                roi_data = {}
                for field, val in roi_form.cleaned_data.items():
                    field = field.split('_')
                    roi_data.setdefault(field[0], {'mean': float(), 'stdev': float(), 'snr': float()})
                    roi_data[field[0]][field[-1]] = val

                measurement = Measurement(
                    modality=form.cleaned_data['modality'], measurement_date=form.cleaned_data['measurement_date'],
                    mas=form.cleaned_data['mas'], entrance_dose=form.cleaned_data['entrance_dose'],
                    comment=form.cleaned_data['comment'], signature=form.cleaned_data['signature']
                )
                measurement.save()

                for ind, obj in roi_data.items():
                    roi_value = RoiValue(
                        measurement=measurement, roi=int(ind),
                        mean=obj['mean'], stdev=obj['stdev'], signal_noise_ratio=obj['snr']
                    )
                    roi_value.save()

                # Redirect to the result view
                return HttpResponseRedirect('mg:mg-weekly-qa-result')
        raise Http404

    modality = request.GET.get('modality', None)
    update_form = request.GET.get('updateForm', None)
    form = MammographyWeeklyQAForm()
    context = {}
    if modality is not None:
        # Get extra fields and information for the measurement form
        try:
            modality = int(modality)
            form.fields['modality'].initial = modality
            modality = Modality.objects.get(id=modality)
            roi_form = ROIForm(rois=modality.number_of_rois)
            context = {'form': form, 'roiForm': {'rois': modality.number_of_rois, 'form': roi_form}}
            if update_form is not None and update_form:
                references = Reference.objects.all().filter(
                    parameter__modality=modality, parameter__active=True, active=True)
                refs = {}
                if len(references) > 0:
                    for obj in references:
                        if obj.tolerance_unit == '%':
                            ref_min = obj.parameter_value * (1 - obj.tolerance / 100)
                            ref_max = obj.parameter_value * (1 + obj.tolerance / 100)
                        else:
                            ref_min = obj.parameter_value - obj.tolerance
                            ref_max = obj.parameter_value + obj.tolerance

                        refs[obj.parameter.parameter] = {'min': ref_min, 'max': ref_max}
                return JsonResponse({'rois': modality.number_of_rois,
                                     'instructions': modality.instructions,
                                     'references': refs})
        except:
            raise

    if len(context) < 1:
        context = {'form': form, 'roiForm': {'rois': 0}}

    return render(request=request, template_name='mammography/mg_measurement_form.html',
                  context=context)


def mgqa_measurement_result(request):

    return render


class MGQAMeasurementForm(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        modality = self.request.query_params.get('modality', None)
        try:
            modality = int(modality)
        except:
            modality = None
        if modality is None:
            handler400 = 'rest_framework.exceptions.bad_request'
            return Response(handler400)

        modality = Modality.objects.get(id=modality)
        form = MammographyWeeklyQAForm()
        roi_form = ROIForm(rois=modality.number_of_rois)

        q = Reference.objects.all().filter(parameter__modality=modality, parameter__active=True, active=True)
        tolerances = {}
        for obj in q:
            tolerances.setdefault(obj.parameter.parameter,
                                  {'tolerance': obj.parameter.tolerance, 'unit': obj.parameter.tolerance_unit})

        return Response({'form': form, 'roiForm': roi_form, 'rois': modality.number_of_rois, 'tolerances': tolerances})


class MGQAResultView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        modality = self.request.query_params.get('modality', None)

        reference = Reference.objects.all().filter(parameter__modality_id=modality, active=True, parameter__active=True)
        roi_value = RoiValue.objects.all().filter(measurement__modality_id=modality)

        reference = ModalityReferenceSerializer(data=reference)
        roi_value = ModalityMeasurementSerializer(data=roi_value)

        Response({'measurement': roi_value, 'reference': reference})
