from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Prefetch, Count, Sum, When, IntegerField
from django.db.models.functions import TruncYear
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from pathlib import Path

from .models import Radiopharmaceutical, Production, Administration, ReadFiles
from .serializers import ProductionSerializer
from .tools.import_production_data import import_production_data


def radpharmstat(request):
    prod_years = list(Production.objects.order_by('-datum').dates('datum', 'year'))
    prod_data = list(set(Production.objects.order_by(
        'radiopharmaceutical__name', '-datum'
    ).annotate(year=TruncYear('datum')).values_list('radiopharmaceutical__name', 'year')))

    start_radiopharmaceutical = Production.objects.filter(
        datum__gte=timezone.now() - relativedelta(years=1)
    ).order_by(
        'radiopharmaceutical__name'
    ).values_list(
        'radiopharmaceutical__name'
    ).distinct()

    prod_years = [obj.year for obj in prod_years]
    prod_years.sort(reverse=True)
    prod_radpharm_by_year = {str(obj): [] for obj in prod_years}
    radiopharmaceutical = []
    for obj in prod_data:
        prod_radpharm_by_year[str(obj[1].year)].append(obj[0])
        radiopharmaceutical.append(obj[0])

    prod_radpharm_by_year['0'] = [obj[0] for obj in start_radiopharmaceutical]

    context = dict(
        years=prod_years,
        year_radpharm=prod_radpharm_by_year,
        radiopharmaceuticals=list(set(radiopharmaceutical)),
        radpharm=prod_radpharm_by_year['0']
    )
    return render(request=request, template_name='radpharmprod/view_statistics.html', context=context)


def api_get_statistics(request):
    time_interval = request.GET.get('timeInterval', None)
    radiopharamaceutical = request.GET.get('radiopharmaceutical', None)

    if time_interval is None or radiopharamaceutical is None:
        return HttpResponseBadRequest

    time_interval = int(time_interval)

    query = Production.objects.filter(radiopharmaceutical__name=radiopharamaceutical)

    if time_interval < 1:
        query = query.filter(datum__gte=timezone.now() - relativedelta(years=1))
    elif time_interval == 1:
        timespan = [obj for obj in request.GET.getlist('timespan')]
        if len(timespan) != 2:
            return HttpResponseBadRequest
        timespan.sort()
        query = query.filter(datum__gte=timespan[0], datum__lte=timespan[1])
    else:
        query = query.filter(datum__year=int(time_interval))

    query = query.all().annotate(count_patients=Count('administration__pk'))

    production = ProductionSerializer(query, many=True)

    return JsonResponse(data=production.data, safe=False)


def api_import_production_data(request):
    import_production_data(Path(settings.RADIOPHARMACEUTICAL_BASE_DIR))
    return redirect('home:home')
