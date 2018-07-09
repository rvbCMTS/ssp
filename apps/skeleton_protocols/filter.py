import django_filters
from .models import Protocols, Machine
from django import forms


class ProtocolsFilter(django_filters.FilterSet):
    ris_name = django_filters.CharFilter(lookup_expr='icontains', label='Protocol')
    machine = django_filters.ModelChoiceFilter(queryset=Machine.objects.all())
    technique = django_filters.AllValuesMultipleFilter(widget=forms.CheckboxSelectMultiple)
    kv = django_filters.NumberFilter(name='kv')
    kv__lt = django_filters.NumberFilter(name='kv', label='Tube Voltage Less Than', lookup_expr='lte')
    kv__gt = django_filters.NumberFilter(name='kv', label='Tube Voltage Greater Than', lookup_expr='gte')
    sensitivity = django_filters.AllValuesMultipleFilter(name='sensitivity',
                                                         widget=forms.CheckboxSelectMultiple
                                                         )

    class Meta:
        model = Protocols
        fields = ['ris_name', 'machine']
        order_by = ['ris_name']
