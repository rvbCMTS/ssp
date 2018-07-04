from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_noop as _
from datetime import datetime as dt

from .models import Exam, AnatomyRegion, Clinic, ClinicCategory, Modality, Operator, OperatorClinicMap, ModalityClinicMap
