from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from math import ceil
import numpy as np
import os
from typing import Any, Dict, List, Optional

from django.db.models.functions import TruncYear
from pandas import DataFrame

from .models import (Result)


def import_personnel_dosimetry_report(vendor: str, input_file_directory: str, output_file_directory: str):
    if not os.path.exists(input_file_directory):
        raise ValueError('The input file directory does not exist')
    if vendor.lower() == 'landauer':
        from .tools.read_landauer_reports import parse_reports
        parse_reports(input_file_directory, output_file_directory)
    else:
        raise NotImplementedError(f'Import of personnel dosimetry reports not implemeted for {vendor}')

    return True


def get_personnel_dosimetry_filter_data(user, time_period_start: dt):
    base_query = Result.objects.filter(measurement_period_center__gte=time_period_start)

    years = [obj['year'].year for obj in
             base_query.annotate(year=TruncYear('measurement_period_center')).order_by(
                 '-year'
             ).values(
                 'year'
             ).distinct()]

    # Get clinics with data in
    clinics = [{'id': obj['clinic__display_name__id'], 'name': obj['clinic__display_name__display_name']} for obj in
               base_query.values(
                   'clinic__display_name__id', 'clinic__display_name__display_name'
               ).distinct()]

    # Get Professions
    profession = [{'id': obj['personnel__profession_id'], 'name': obj['personnel__profession__profession']} for obj in
                  base_query.values(
                      'personnel__profession__profession', 'personnel__profession_id'
                  ).order_by(
                      'personnel__profession__profession'
                  ).distinct()
                  ]

    # Get personnel list
    personnel = base_query.values('personnel_id', 'personnel__person_name').distinct()

    if user.has_perm('personnel_dosimetry.view_personnel_names'):
        personnel = [{'id': obj['personnel_id'], 'name': f"{obj['personnel__person_name']} ({obj['personnel_id']})"}
                     for obj in personnel.order_by('personnel__person_name')]
    else:
        personnel = [{'id': obj['personnel_id'], 'name': obj['personnel_id']} for obj in
                     personnel.order_by('personnel_id')]

    # Get a list of dosimeter placements
    dp = [{'id': obj['vendor_dosimetry_placement__dosimeter_placement_id'],
           'placement': obj['vendor_dosimetry_placement__dosimeter_placement__dosimeter_placement']} for obj in
          base_query.values(
              'vendor_dosimetry_placement__dosimeter_placement__dosimeter_placement',
              'vendor_dosimetry_placement__dosimeter_placement_id'
          ).order_by(
              'vendor_dosimetry_placement__dosimeter_placement__dosimeter_placement'
          ).distinct()]

    return {
        'filter_years': years,
        'clinic': clinics,
        'personnel_category': profession,
        'personnel': personnel,
        'dosimeter_placement': dp
    }


def _format_personnel_dosimetry_plot(data: DataFrame, plot_id: str, plot_title: str, y_range: List[float]):
    """Format the data frame data into the format required for Plotly.js

    :param data: DataFrame of data to format according to Plotly.js requirements
    :param plot_id: The HTML id of the plot for which data is to be formatted
    :param plot_title: The title of the plot
    :param y_range: The range in the y-axis to use for the plot
    :return:
    """
    plot_data = [
        {
            'x': list(data.columns),
            'y': [el if el is None or not np.isnan(el) else None for el in row[1:]],
            'name': row.Index,
            'mode': 'markers',
            'text': [row.Index] * len(list(data.columns)),
            'type': 'scatter',
            'hoverinfo': 'y+text'
        }
        for row in data.itertuples()
    ]

    plot = {
        'id': plot_id,
        'data': plot_data,
        'layout': {
            'xaxis': {
                'title': 'Datum'
            },
            'yaxis': {
                'title': f'{plot_title} [mSv]',
                'range': y_range
            },
            'title': plot_title,
            'showlegend': False,
            'hoverinfo': 'y+name'
        },
        'layout2': {
            'displayModeBar': False,
            'displaylogo': False
        }
    }

    return plot


def _format_personnel_dosimetry_table_data(data: DataFrame) -> List[List[str]]:
    return [['test']]


def _get_plot_and_table_data_query(time_interval: int, clinic: Optional[int] = None, profession: Optional[int] = 0,
                                   personnel: Optional[int] = 0, dosimeter_placement: Optional[int] = 0,
                                   exclude_spot_check: Optional[bool] = True,
                                   exclude_area_measurement: Optional[bool] = True):
    query = Result.objects

    if time_interval > 2000:
        query = query.filter(measurement_period_center__year=time_interval)
    else:
        if time_interval < 1:
            time_interval = 1
        query = query.filter(measurement_period_center__gte=(dt.now() - relativedelta(years=time_interval)))

    if clinic is None or clinic < 1:
        return query

    # Add clinic filter
    query = query.filter(clinic__display_name_id__exact=clinic)

    # Add profession filter
    if profession > 0:
        query = query.filtetr(personnel__profession_id__exact=profession)

    # Add personnel filter
    if personnel > 0:
        query = query.filter(personnel_id__exact=personnel)

    # Add dosimeter placement filter
    if dosimeter_placement > 0:
        query = query.filter(vendor_dosimetry_placement__dosimeter_placement_id__exact=dosimeter_placement)

    # Add Spotcheck filter
    if exclude_spot_check:
        query = query.filter(spot_check=False)

    if exclude_area_measurement:
        query = query.filter(area_measurement=False)

    query = query.select_related(
            'vendor_dosimetry_placement__dosimeter_placement'
        ).select_related(
            'personnel'
        ).select_related(
            'clinic__display_name'
        ).select_related(
            'personnel__profession'
        ).all()

    return query


def get_plot_and_table_data(user, time_interval: int, clinic: Optional[int] = None, profession: Optional[int] = 0,
                            personnel: Optional[int] = 0, dosimeter_placement: Optional[int] = 0,
                            exclude_spot_check: Optional[bool] = True,
                            exclude_area_measurement: Optional[bool] = True) -> DataFrame:
    query = _get_plot_and_table_data_query(time_interval=time_interval, clinic=clinic, profession=profession,
                                           personnel=personnel, dosimeter_placement=dosimeter_placement,
                                           exclude_spot_check=exclude_spot_check,
                                           exclude_area_measurement=exclude_area_measurement)
    df = DataFrame([{
        'Personnel': qo.personnel.person_name,
        'PersonnelAnon': qo.personnel_id,
        'DosimetryPlacement': qo.vendor_dosimetry_placement.dosimeter_placement.dosimeter_placement,
        'VendorDosimetryPlacement': qo.vendor_dosimetry_placement.vendor_dosimeter_placement,
        'DosimeterLaterality': qo.vendor_dosimetry_placement.dosimeter_laterality.dosimeter_laterality,
        'PeriodCenter': qo.measurement_period_center,
        'Hp10': qo.hp10,
        'Hp007': qo.hp007,
        'Hp10tn': qo.hp10tn,
        'Hp10fn': qo.hp10fn,
    } for qo in query])

    if user.has_perm('personnel_dosimetry.view_personnel_names'):
        df['PersonnelDisplayName'] = df.Personnel + ' (' + df.PersonnelAnon.map(str) + ')' + ' ' + df.DosimetryPlacement + ', ' + df.DosimeterLaterality
    else:
        df['PersonnelDisplayName'] = df.PersonnelAnon + ' ' + df.DosimetryPlacement + ', ' + df.DosimeterLaterality

    return df


def format_plot_and_table_data(data: DataFrame) -> Dict[str, Any]:
    plot_data = []
    table_data = []

    # FORMAT PLOT DATA
    # Define the range for each plot
    hp10_max, hp007_max, hp10tn_max, hp10fn_max = (
        data.Hp10.max(), data.Hp007.max(), data.Hp10tn.max(), data.Hp10fn.max())

    plot_ranges = {
        'Hp10': [-0.05, (1.0 if np.isnan(hp10_max) or hp10_max < 1 else ceil(hp10_max))],
        'Hp007': [-0.05, (1.0 if np.isnan(hp007_max) or hp007_max < 1 else ceil(hp007_max))],
        'Hp10tn': [-0.05, (1.0 if np.isnan(hp10tn_max) or hp10tn_max < 1 else ceil(hp10tn_max))],
        'Hp10fn': [-0.05, (1.0 if np.isnan(hp10fn_max) or hp10fn_max < 1 else ceil(hp10fn_max))]
    }

    plot_data = data.pivot(index='PersonnelDisplayName', columns='PeriodCenter',
                           values=['Hp10', 'Hp007', 'Hp10tn', 'Hp10fn'])
    output_plots = [
        _format_personnel_dosimetry_plot(data=plot_data.Hp10, plot_id='hp10Plot', plot_title='Hp(10)',
                                         y_range=plot_ranges['Hp10']),
        _format_personnel_dosimetry_plot(data=plot_data.Hp007, plot_id='hp007Plot', plot_title='Hp(0,07)',
                                         y_range=plot_ranges['Hp007']),
        _format_personnel_dosimetry_plot(data=plot_data.Hp10tn, plot_id='hp10tnPlot', plot_title='Hp(10)tn',
                                         y_range=plot_ranges['Hp10tn']),
        _format_personnel_dosimetry_plot(data=plot_data.Hp10fn, plot_id='hp10fnPlot', plot_title='Hp(10)fn',
                                         y_range=plot_ranges['Hp10fn']),
    ]

    # FORMAT TABLE DATA
    table_data = data[['PersonnelDisplayName', 'Hp10', 'Hp007', 'Hp10tn', 'Hp10fn']].groupby(
        by='PersonnelDisplayName'
    ).sum(axis=0, skipna=True)
    table_data_all_nan = data[['PersonnelDisplayName', 'Hp10', 'Hp007', 'Hp10tn', 'Hp10fn']].groupby(
        by='PersonnelDisplayName'
    ).apply(lambda x: x.isnull().all())
    table_data[table_data_all_nan] = None

    output_table_data = [[
        row.Index,
        (f"{row.Hp10:.2f}" if not np.isnan(row.Hp10) else "-"),
        (f"{row.Hp007:.2f}" if not np.isnan(row.Hp007) else "-"),
        (f"{row.Hp10tn:.2f}" if not np.isnan(row.Hp10tn) else "-"),
        (f"{row.Hp10fn:.2f}" if not np.isnan(row.Hp10fn) else "-")
    ] for row in table_data.itertuples()]

    return {'plotData': output_plots, 'tableData': {'data': output_table_data}}
