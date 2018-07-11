from datetime import datetime as dt
from django.db.models import Count
import logging
import numpy as np
import os
import pandas as pd
from uuid import uuid4

from ..models import Profession, Result, Clinic, Personnel, VendorDosimeterPlacement


def parse_reports(input_file_directory: str, output_file_directory: str):
    if not isinstance(input_file_directory, str) or not isinstance(output_file_directory, str):
        raise TypeError((f'Both the input and output directory must be paths to directories given as string.\n'
                         f'\tType input: {type(input_file_directory)})\n'
                         f'\tType output: {type(output_file_directory)}'))
    if not os.path.exists(input_file_directory) or not os.path.isdir(input_file_directory):
        raise ValueError(f'The given input directory is not a valid directory ({input_file_directory})')

    log = logging.getLogger(__name__)

    original_reports = _find_reports('ORIGINAL', input_file_directory, log)
    new_reports = _find_reports('NEW', input_file_directory, log)

    log.info(f'Found {len(original_reports) + len(new_reports)} reports')
    if len(original_reports) > 0:
        results, not_returned = _clean_input_data(original_reports, log)
        log.debug(f'Finished importing {len(original_reports)} Landauer personnel dosimetry reports')

        if _insert_results_to_db(results, 'ORIGINAL', log):
            _move_handled_files(original_reports, output_file_directory, log)

    if len(new_reports) > 0:
        results, not_returned = _clean_input_data(new_reports, log)
        log.debug(f'Finished importing {len(new_reports)} Landauer personnel dosimetry reports')

        if _insert_results_to_db(results, 'NEW', log):
            _move_handled_files(new_reports, output_file_directory, log)

    return True


def _find_reports(report_type: str, input_file_directory: str, log: logging.Logger) -> list:
    """ Go through the input_file_directory and find all personnel dosimetry reports of the specified type

    :param report_type: 'ORIGINAL' or 'NEW' for separating the files that only contain updates from the reports
                        containing all personnel for that measurement period
    :param input_file_directory: Path to directory containing dose report files to be parsed
    :return: List of file paths to *.xls and *.xlsx files found in input_file_directory
    """
    reports = []

    # List file paths to original or new reports depending on input report_type
    if report_type.upper() == 'ORIGINAL':
        log.debug('Searching for original Landauer reports')
        reports = [os.path.join(input_file_directory, filename) for filename in os.listdir(input_file_directory) if
                   (filename.lower().endswith('.xls') or filename.lower().endswith('.xlsx'))
                   and 'NEW' not in filename.upper()]

    elif report_type.upper() == 'NEW':
        log.debug('Searching for Landauer reports marked as new')
        reports = [os.path.join(input_file_directory, filename) for filename in os.listdir(input_file_directory) if
                   (filename.lower().endswith('.xls') or filename.lower().endswith('.xlsx'))
                   and 'NEW' in filename.upper()]

    log.debug('Finished search for Lnadauer personnel dosimetry reports')
    return reports


def _clean_input_data(report_list: list, log: logging.Logger):
    """

    :param report_list:
    :param log:
    :return:
    """
    col_names_report = ['Kundtext', 'Kundtext 2', 'Kundnummer', 'Underavdelningsnr', 'Avdelningsnummer', 'Deltagar-id',
                        'Personnummer', 'Namn', 'Yrkeskod', 'Hp(10)', 'Hp(0,07)', 'Hp(10) thermal n', 'Hp(10) fast n',
                        'Dosimetertyp', 'Dosimeterplacering', 'Servicekod', 'Startdatum - mätperiod',
                        'Slutdatum - mätperiod', 'Rapportdatum', 'Rapport nr', 'Rapport version']

    col_names = ['Kundtext1', 'Kundtext2', 'Kundnummer', 'Underavdelningsnr', 'Avdelningsnummer', 'DeltagarId',
                 'Personnummer', 'Namn', 'Yrkeskod', 'Hp10', 'Hp007', 'Hp10tn', 'Hp10fn', 'Dosimetertyp',
                 'Dosimeterplacering', 'Servicekod', 'Startdatum', 'Slutdatum', 'Rapportdatum', 'Rapportnr',
                 'RapportVersion']

    np_concat = np.vectorize(_concat)

    # Create a new empty data frame
    df = pd.DataFrame(columns=col_names)

    # Import data from reports
    log.info('Start importing data from Landauer personnel dosimetry reports')
    n = 0
    for report in report_list:
        n += 1
        log.debug(f'Importing file {n} out of {len(report_list)}')
        dftmp = pd.read_excel(report)
        if 'Hp(10) thermal n' not in list(dftmp.columns):
            dftmp['Hp(10) thermal n'] = np.nan
            dftmp['Hp(10) fast n'] = np.nan
        if 'Yrkeskod' not in list(dftmp.columns):
            dftmp['Yrkeskod'] = np.nan

        if 'Kundtext 1' in list(dftmp.columns):
            col_names_report[0] = 'Kundtext 1'
        else:
            col_names_report[0] = 'Kundtext'

        dftmp = dftmp[col_names_report]
        dftmp.rename(columns={old: col_names[ind] for ind, old in enumerate(col_names_report)}, inplace=True)
        df = df.append(dftmp, ignore_index=True)

    df.Hp10tn = df.Hp10tn.astype(str)
    df.Hp10fn = df.Hp10fn.astype(str)

    # Only keep newest version of each report
    log.info('Filter out older version of the reports if multiple versions present in the imported data')
    df['concat'] = np_concat(df['Rapportnr'], df['RapportVersion'])
    rnr = np.unique(df.Rapportnr)
    rver = [f'{x}, {max(df.RapportVersion[df.Rapportnr == x])}' for x in rnr]
    df['Keep'] = [True if df.concat[ind] in rver else False for ind in df.index]
    df = df[df.Keep]
    df.index = range(len(df.ix[:, 0]))  # Resets index on data frame

    # Replace 'M' (which means below lowest measurable value) with 0 and find which rows contain 'NR'
    log.info('Replace the "M" that marks measurements below the detection limit with "0"')
    try:
        df.Hp10.replace(['M', ''], ['0', '0'], inplace=True)
        df.Hp007.replace(['M', ''], ['0', '0'], inplace=True)
        df.Hp10tn.replace('M', '0', inplace=True)
        df.Hp10fn.replace('M', '0', inplace=True)
        mask = [
            True if (row.Hp10 == 'NR') or (row.Hp007 == 'NR') or (row.Hp10tn == 'NR') or (row.Hp10fn == 'NR') else False
            for _, row in df.iterrows()]
    except TypeError:
        pass

    log.info('Separating the dosimeters that have not been returned from the returned ones')
    df_nr = df[mask].copy()
    df_nr.index = range(len(df_nr.ix[:, 0]))  # Resets index on data frame
    df = df[[False if i else True for i in mask]]
    df.index = range(len(df.ix[:, 0]))  # Resets index on data frame

    # Remove other values than nan or floats
    df.Hp10 = df.Hp10.str.replace(',', '.')
    df.Hp007 = df.Hp007.str.replace(',', '.')
    df.Hp10tn = df.Hp10tn.str.replace(',', '.')
    df.Hp10fn = df.Hp10fn.str.replace(',', '.')
    df['Hp10String'] = [_float_conversion_test(val) for val in df.Hp10]
    df['Hp007String'] = [_float_conversion_test(val) for val in df.Hp007]
    df['Hp10tnString'] = [_float_conversion_test(val) for val in df.Hp10tn]
    df['Hp10fnString'] = [_float_conversion_test(val) for val in df.Hp10fn]
    df = df[
        [False if (row.Hp10String + row.Hp007String + row.Hp10fnString + row.Hp10tnString) > 0 else True for _, row in
         df.iterrows()]]
    df.index = range(len(df.ix[:, 0]))  # Resets index on data frame

    return df, df_nr


def _insert_results_to_db(results: pd.DataFrame, list_type: str, log: logging.Logger):
    """ Take the parsed Landauer personnel dosimetry results in the form of a Pandas DataFrame. Check which db reports
    should be added/update. Perform database upsert queries

    :param results:
    :param log:
    :return:
    """
    # Check which reports already have a version in the database
    report_in_db = [obj['report'] for obj in Result.objects.all().annotate(dcount=Count('report')).values('report')]
    db_report_numbers = [obj.split(':')[0] for obj in report_in_db]
    db_report_versions = [obj.split(':')[1] for obj in report_in_db]

    # Find which versions of reports are new
    if list_type.upper() == 'ORIGINAL':
        results.Keep = [True if (
                f'{row.Rapportnr}' not in db_report_numbers or f'{row.RapportVersion}' > db_report_versions[
                    db_report_numbers.index(f'{row.Rapportnr}')]) else False for _, row in results.iterrows()]
    else:
        results.Keep = [True if (
                f'{row.Rapportnr}' not in db_report_numbers or f'{row.RapportVersion}' >= db_report_versions[
                    db_report_numbers.index(f'{row.Rapportnr}')]) else False for _, row in results.iterrows()]

    # Remove reports already present in the database
    results = results[results.Keep]
    results.index = range(len(results.ix[:, 0]))  # Resets index on data frame

    if len(results) < 1:
        return True

    # Find new personnel
    log.info('Checking if there are any new personnel to be added to the database')
    personnel_in_db = pd.DataFrame(list(Personnel.objects.all().values()))
    vendor_dosimeter_placement_in_db = pd.DataFrame(list(VendorDosimeterPlacement.objects.all().values()))
    clinics_in_db = pd.DataFrame(list(Clinic.objects.all().values()))

    #if len(personnel_in_db) > 0:
    #    results['newpers'] = [0 if str(row.DeltagarId) in personnel_in_db.dosimetry_vendor_id.values else
    #                          (1 if (str(row.Personnummer).strip() in personnel_in_db.person_id.values) else 2)
    #                          for _, row in results.iterrows()]
    #else:
    #    results['newpers'] = [0] * len(results)

    for _, row in results.iterrows():
        # Get Personnel object
        if len(personnel_in_db) < 1 or str(row.DeltagarId) not in personnel_in_db.dosimetry_vendor_id.values:
            if not np.isnan(row.Yrkeskod):
                profession = Profession.objects.get(landauer_profession_id=int(row.Yrkeskod))
            else:
                profession = None

            personnel = Personnel(dosimetry_vendor_id=row.DeltagarId, person_id=row.Personnummer,
                                  person_name=row.Namn.title(), profession=profession)
            personnel.save()
            personnel_in_db = pd.DataFrame(list(Personnel.objects.all().values()))
            #results['newpers'] = [0 if str(row2.DeltagarId) in personnel_in_db.dosimetry_vendor_id.values else
            #                     (1 if (row2.Personnummer in personnel_in_db.person_id.values) else 2)
            #                      for _, row2 in results.iterrows()]
        else:
            personnel = Personnel.objects.get(dosimetry_vendor_id=row.DeltagarId)
            if len(str(row.Personnummer).strip()) > 0 and str(row.Personnummer).strip() not in personnel_in_db.person_id.values:
                personnel.person_id = row.Personnummer
                personnel.save()
            if personnel.profession is None and not np.isnan(row.Yrkeskod):
                profession = Profession.objects.get(landauer_profession_id=int(row.Yrkeskod))
            else:
                profession = None
            if profession is not None:
                personnel.profession = profession
                personnel.save()

        # Get vendor dosimeter placement
        if len(vendor_dosimeter_placement_in_db) < 1 or str(row.Dosimeterplacering).strip() not in vendor_dosimeter_placement_in_db.vendor_dosimeter_placement.values:
            vdp = VendorDosimeterPlacement(vendor_dosimeter_placement=str(row.Dosimeterplacering).strip())
            vdp.save()
            vendor_dosimeter_placement_in_db = pd.DataFrame(list(VendorDosimeterPlacement.objects.all().values()))
        else:
            vdp = VendorDosimeterPlacement.objects.get(vendor_dosimeter_placement=str(row.Dosimeterplacering).strip())

        # Get clinic
        clinic_string = (f'{str(row.Kundnummer).strip()}:{str(row.Avdelningsnummer).strip()}:{str(row.Underavdelningsnr).strip()} '
                         f'{str(row.Kundtext1).strip()} - {str(row.Kundtext2).strip()}')

        if len(clinics_in_db) < 1 or clinic_string not in clinics_in_db.clinic.values:
            clinic = Clinic(clinic=clinic_string, display_clinic=clinic_string)
            clinic.save()
            clinics_in_db = pd.DataFrame(list(Clinic.objects.all().values()))
        else:
            clinic = Clinic.objects.get(clinic=clinic_string)

        start_date = dt.strptime(row.Startdatum, '%Y-%m-%d')
        stop_date = dt.strptime(row.Slutdatum, '%Y-%m-%d')

        # Save new measurement to database
        db_result = Result(dosimetry_vendor='Landauer', personnel=personnel, vendor_dosimetry_placement=vdp,
                           clinic=clinic, report=f'{row.Rapportnr}:{row.RapportVersion}',
                           measurement_period_start=row.Startdatum, measurement_period_stop=row.Slutdatum,
                           measurement_period_center=(start_date + (stop_date - start_date) / 2),
                           hp10=row.Hp10, hp007=row.Hp007, hp10fn=row.Hp10fn, hp10tn=row.Hp10tn,
                           dosimeter_type=row.Dosimetertyp)
        db_result.save()

    return True


def _move_handled_files(input_paths: str, output_folder: str, log: logging.Logger):
    """Take the input paths and move the files into the output folder

    :param input_paths: List of full paths to the files that are to be moved
    :param output_folder: The folder into which the files should be moved
    """
    log.info(f'Moving parsed Landauer dosimetry files to "{output_folder}"')
    for f in input_paths:
        if os.path.isfile(f):
            os.replace(src=f, dst=os.path.join(output_folder, os.path.basename(f)))


# Create concatenation function for concatenating DataFrame columns
def _concat(*args):
    strings = [str(arg) for arg in args if not pd.isnull(arg)]
    return ', '.join(strings) if strings else np.nan


def _float_conversion_test(string_to_convert):
    """Take the string that should be converted to a float. Try to convert it. If successful return 0 else return 1.
    """
    try:
        _ = float(string_to_convert)  # Try to convert string
        return 0
    except:
        return 1
