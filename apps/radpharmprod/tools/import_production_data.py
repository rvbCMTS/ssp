from datetime import datetime
import json
import numpy as np
import pandas as pd
from pathlib import Path, PurePath
from typing import Optional, List, Union
from xlrd import XLRDError

from ..models import ReadFiles, Radiopharmaceutical, Production, Administration


class RadPharmAdministration:
    def __init__(self, patient_weight: float, desired_administration_time: datetime, desired_administration: float,
                 activity_in_syringe: float, activity_in_syringe_time: datetime,
                 activity_left_in_syringe: float, activity_left_in_syringe_time: datetime):
        self.PatientWeight: float = patient_weight
        self.DesiredAdministrationTime: datetime.time = desired_administration_time
        self.DesiredAdministration: float = desired_administration
        self.ActivityInSyringeTime: datetime.time = activity_in_syringe_time
        self.ActivityInSyringe: float = activity_in_syringe
        self.ActivityLeftInSyringeTime: datetime.time = activity_left_in_syringe_time
        self.ActivityLeftInSyringe: float = activity_left_in_syringe


class RadPharmProduction:
    def __init__(self, radiopharmaceutical: str, radiopharmaceutical_path: Path):
        self.Radiopharmaceutical: Union[str, Radiopharmaceutical] = radiopharmaceutical
        self.Directory: Path = radiopharmaceutical_path
        self.ProductionDate: datetime = None
        self.Activity: float = None
        self.Volume: float = None
        self.Batch: str = None
        self.Signature: str = None
        self.Administration: List[RadPharmAdministration] = []
        self.SuccessfulImport: bool = False

    def import_file(self):
        try:
            df = pd.read_excel(io=self.Directory, sheet_name='Administrering', header=None,
                               names=['key', 'val', 'na1', 'na2', 'unit'],
                               usecols='B:F', skiprows=5, nrows=5)

            self.ProductionDate = df.val[0]
            self.Activity = df.val[1]
            self.Volume = df.val[2]
            self.Batch = df.val[3]
            self.Signature = df.val[4]

            df = pd.read_excel(io=self.Directory, sheet_name='Administrering', header=None,
                               names=['weight', 'WishedDoseTime', 'WishedDose', 'na1', 'na2', 'na3',
                                      'ActivityInSyringe', 'ActivityInSyringeTime',
                                      'LeftInSyringe', 'LeftInSyringeTime'],
                               usecols='I:R', skiprows=5, nrows=16)

            for ind, row in df.iterrows():
                if not isinstance(row.ActivityInSyringe, float) and not isinstance(row.ActivityInSyringe, int) or \
                        np.isnan(row.ActivityInSyringe):
                    continue
                try:
                    weight = float(row.weight)
                except:
                    weight = None
                try:
                    activity_in_syringe = float(row.ActivityInSyringe)
                except:
                    activity_in_syringe = None
                try:
                    left_in_syringe = float(row.LeftInSyringe)
                except:
                    left_in_syringe = None

                self.Administration.append(
                    RadPharmAdministration(
                        patient_weight=weight,
                        desired_administration=float(row.WishedDose),
                        desired_administration_time=row.WishedDoseTime,
                        activity_in_syringe=activity_in_syringe,
                        activity_in_syringe_time=row.ActivityInSyringeTime,
                        activity_left_in_syringe=left_in_syringe,
                        activity_left_in_syringe_time=row.LeftInSyringeTime
                    )
                )

            self.SuccessfulImport = True
        except XLRDError as e:
            self.SuccessfulImport = False
            raise
        except Exception as e:
            self.SuccessfulImport = False
            raise

        if self.ProductionDate is None or (
                not isinstance(self.ProductionDate, datetime)
        ) or (
                not (isinstance(self.Activity, float) or isinstance(self.Activity, int)) or not (
                isinstance(self.Volume, float) or isinstance(self.Volume, int))
        ):
            self.ProductionDate = None
            self.Activity = None
            self.Volume = None
            self.Administration = None
            self.SuccessfulImport = False
            raise ValueError('Missing value')


def import_production_data(base_dir: Path):
    """ Go through the base directory, find production log files, read data, save data to database

    :param base_dir: Path object of directory containing production excel log files
    :return:
    """
    EXCLUDE_FOLDER_NAMES = ["Statistik", "GamlaMallar", "GAMMALT", "Gamla mallar"]
    radiopharmaceuticals = [x for x in base_dir.iterdir() if x.is_dir() and x.stem not in EXCLUDE_FOLDER_NAMES]

    rp_in_db = [obj.name for obj in Radiopharmaceutical.objects.all()]
    not_in_db = list(set([rp.stem for rp in radiopharmaceuticals]) - set(rp_in_db))
    if len(not_in_db) > 0:
        rpobj = [Radiopharmaceutical(name=rp) for rp in not_in_db]
        Radiopharmaceutical.objects.bulk_create(objs=rpobj)

    read_files = [f for f in ReadFiles.objects.filter(successful=True).values_list('file', flat=True)]

    production_list: List[RadPharmProduction] = []

    for rp in radiopharmaceuticals:
        data_dirs = [x for x in rp.iterdir() if x.is_dir() and x.stem not in EXCLUDE_FOLDER_NAMES]
        for data_dir in data_dirs:
            data_files = [xlsfile for xlsfile in data_dir.glob('*.xls')] + [xlsfile for xlsfile in
                                                                            data_dir.glob('*.xlsx')]

            data_files = [x for x in data_files if str(x.absolute()) not in read_files]

            if len(data_files) < 1:
                continue

            for data_file in data_files:
                try:
                    tmp = RadPharmProduction(radiopharmaceutical=rp.stem, radiopharmaceutical_path=data_file)
                    tmp.import_file()
                    if tmp.SuccessfulImport:
                        production_list.append(tmp)
                except Exception as e:
                    ReadFiles.objects.update_or_create(
                        file=data_file,
                        defaults={'radiopharmaceutical': Radiopharmaceutical.objects.get(name=rp.stem),
                                  'successful': False}
                    )

    if len(production_list) < 1:
        return True

    for production in production_list:
        rp = Radiopharmaceutical.objects.get(name=production.Radiopharmaceutical)
        try:
            prod, created = Production.objects.update_or_create(
                batch=production.Batch,
                radiopharmaceutical=rp,
                defaults={
                    'datum': production.ProductionDate,
                    'activity_mbq': production.Activity,
                    'volume_ml': production.Volume,
                    'signature': production.Signature
                }
            )
        except:
            continue

        if created:
            for administration in production.Administration:
                if not isinstance(administration.ActivityLeftInSyringeTime, datetime):
                    administration.ActivityLeftInSyringeTime = None

                if not isinstance(administration.ActivityInSyringeTime, datetime):
                    administration.ActivityInSyringeTime = None

                try:
                    _, _ = Administration.objects.get_or_create(
                        production=prod,
                        patient_weight=administration.PatientWeight,
                        desired_administration_time=administration.DesiredAdministrationTime,
                        desired_activity=administration.DesiredAdministration,
                        activity_in_syringe_time=administration.ActivityInSyringeTime,
                        activity_in_syringe=administration.ActivityInSyringe,
                        activity_left_in_syringe_time=administration.ActivityLeftInSyringeTime,
                        activity_left_in_syringe=administration.ActivityLeftInSyringe
                    )
                except Exception as e:
                    print('An error occurred')

        ReadFiles.objects.update_or_create(
            file=production.Directory,
            defaults={'radiopharmaceutical': rp,
                      'successful': True}
        )






