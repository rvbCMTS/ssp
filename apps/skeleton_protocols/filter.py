import django_filters
from .models import Protocol, Machine


class ProtocolsFilter(django_filters.FilterSet):
    ris_name = django_filters.CharFilter(lookup_expr='icontains', label='Protocol')
    exam_name = django_filters.AllValuesFilter(field_name='exam_name',  label='Exam', empty_label="Exam")
    fp_set = django_filters.AllValuesFilter(field_name='fp_set', empty_label='Gml')
    machine = django_filters.ModelChoiceFilter(queryset=Machine.objects.all(), empty_label="Alla lab")
    technique = django_filters.AllValuesFilter(empty_label="Teknik")
    kv_max = django_filters.AllValuesFilter(field_name='kv', label='kV Max', lookup_expr='lte', empty_label='kV max')
    kv_min = django_filters.AllValuesFilter(field_name='kv', label='Rörspänning', lookup_expr='gte', empty_label='kV min')
    mas_max = django_filters.AllValuesFilter(field_name='mas', label='mAs Max', lookup_expr='lte', empty_label='mAs max')
    mas_min = django_filters.AllValuesFilter(field_name='mas', label='mAs Min', lookup_expr='gte', empty_label='mAs min')
    sensitivity = django_filters.AllValuesFilter(field_name='sensitivity', empty_label='Sensitivity')
    filter_cu = django_filters.AllValuesFilter(field_name='filter_cu', empty_label='Kopparfilter')
    focus = django_filters.AllValuesFilter(field_name='focus', empty_label='Fokus')
    grid = django_filters.AllValuesFilter(field_name='grid', empty_label='Raster')
    lut = django_filters.AllValuesFilter(field_name='lut', empty_label='Lut')
    diamond_view = django_filters.AllValuesFilter(label='Diamond View', empty_label='Diamond View')
    image_auto_amplification = django_filters.AllValuesFilter(label='Amp auto', empty_label='Auto Amp')
    harmonization_kernel_size_max = django_filters.AllValuesFilter(field_name='harmonization_kernel_size', label='Harmonization size', lookup_expr='lte', empty_label='Harm K max')
    harmonization_kernel_size_min = django_filters.AllValuesFilter(field_name='harmonization_kernel_size', label='Harmonization size', lookup_expr='gte', empty_label='Harm K min')
    harmonization_gain_max = django_filters.AllValuesFilter(field_name='harmonization_gain', label='Harmonization gain', lookup_expr='lte', empty_label='Harm G max')
    harmonization_gain_min = django_filters.AllValuesFilter(field_name='harmonization_gain', label='Harmonization gain', lookup_expr='gte', empty_label='Harm G min')
    edge_filter_kernel_size_max = django_filters.AllValuesFilter(field_name='edge_filter_kernel_size', label='Edge size', lookup_expr='lte', empty_label='Edge K max')
    edge_filter_kernel_size_min = django_filters.AllValuesFilter(field_name='edge_filter_kernel_size', label='Edge size', lookup_expr='gte', empty_label='Edge K min')
    edge_filter_gain_max = django_filters.AllValuesFilter(field_name='edge_filter_gain', label='Edge gain', lookup_expr='gte', empty_label='Edge G max')
    edge_filter_gain_min = django_filters.AllValuesFilter(field_name='edge_filter_gain', label='Edge gain', lookup_expr='lte', empty_label='Edge G min')

    class Meta:
        model = Protocol
        fields = ['ris_name', 'machine', 'technique', 'kv', 'sensitivity', 'mas', 'filter_cu']
