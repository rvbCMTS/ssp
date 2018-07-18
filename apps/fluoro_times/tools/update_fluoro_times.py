import datetime as dt
from dateutil import relativedelta
from django.conf import settings
import logging
import math
import numpy as np
import pandas as pd
import pyodbc
import time

from ..models import Exam, ExamDescription, DirtyClinic, DirtyOperator, DirtyModality, Updates


class OrbitGML:
    def __init__(self):
        self.success = False
        self.orbit_data = pd.DataFrame  # Data Frame att stoppa in data från Orbit i
        self.ssp_data = pd.DataFrame  # Data Frame att stopp in data från strålskyddsportalen i
        self.output_data = pd.DataFrame  # Data Frame for the formatted output data

        self.log = logging.getLogger(__name__)

        if settings.FLUORO_TIME_DB_ENGINE['Trusted_Connection']:
            self.orbit_conntection_string = (f'DRIVER={settings.FLUORO_TIME_DB_ENGINE["DRIVER"]};'
                                             f'SERVER={settings.FLUORO_TIME_DB_ENGINE["SERVER"]};'
                                             f'DATABASE={settings.FLUORO_TIME_DB_ENGINE["DATABASE"]};'
                                             f'Trusted_Connection=yes;')
        else:
            self.orbit_conntection_string = (f'DRIVER={settings.FLUORO_TIME_DB_ENGINE["DRIVER"]};'
                                             f'SERVER={settings.FLUORO_TIME_DB_ENGINE["SERVER"]};'
                                             f'DATABASE={settings.FLUORO_TIME_DB_ENGINE["DATABASE"]};'
                                             f'UID={settings.FLUORO_TIME_DB_ENGINE["UID"]};'
                                             f'PWD={settings.FLUORO_TIME_DB_ENGINE["PWD"]};')
        self.orbit_table = settings.FLUORO_TIME_ORBIT_TABLE

        query = Updates.objects.all().filter(server=settings.FLUORO_TIME_DB_ENGINE['SERVER'], successful=True).values('updated').first()
        if query is not None:
            self.start_date = query[0]
        else:
            self.start_date = None

        self.log.info("Start updating data from Orbit")

    def fetch_orbit_data(self):
        """ Fetch data from the Orbit database. Add the fetched data as a data frame to self.orbit_data
        """
        conn = pyodbc.connect(self.orbit_conntection_string)
        query = "SELECT * FROM " + self.orbit_table
        if self.start_date is not None and self.start_date != '':
            start_date: dt.datetime = self.start_date - relativedelta(days=3)
            query += f" WHERE OpDatum >= '{start_date.strftime('%Y-%m-%d')}'"
        self.orbit_data = pd.read_sql_query(query, conn)
        self.orbit_data.columns = [c.replace(' ', '_').replace('-', '_').replace('(', '_').replace(')', '_')
                                   for c in self.orbit_data.columns]
        self.orbit_data = self.orbit_data[self.orbit_data.C_båge.notnull() | self.orbit_data.O_arm.notnull()]
        replacements = {
            'Minuter': {',': '.'},
            'Sekunder': {',': '.'},
            'Total_dos_mGym2_': {',': '.'},
            'Minuter_o': {',': '.'},
            'Sekunder_o': {',': '.'},
            'DAP_mGycm2_': {',': '.'},
            'DLP_mGycm_': {',': '.'}
        }
        self.orbit_data.replace(replacements, regex=True, inplace=True)
        convert_columns = ['Minuter', 'Sekunder', 'Total_dos_mGym2_',
                           'Minuter_o', 'Sekunder_o', 'DAP_mGycm2_', 'DLP_mGycm_']
        for colname in convert_columns:
            self.orbit_data[colname] = pd.to_numeric(self.orbit_data[colname], errors='coerce')

        conn.close()

    def format_data(self):
        """ Reformat the data to fit the output format
        """
        output_data = [[i.Behandlingsnr, i.Opkort_huvudgrupp + ', ' + i.Opkort_undergrupp + ', ' + i.Opkortsbenämning,
                        i.Opdatum, i.Opererande_enhet + ', ' + i.Opavdelning, i.Huvudoperatör, i.C_båge, i.O_arm,
                        i.Minuter + i.Sekunder / 60, i.Minuter_o + i.Sekunder_o / 60, i.Total_dos_mGym2_, i.DAP_mGycm2_]
                       for i in self.orbit_data.itertuples()]
        column_names = ['examNo', 'examDescId', 'examDate', 'clinicId', 'operatorId', 'idModality1', 'idModality2',
                        'fluoroTime1', 'fluoroTime2', 'dose1', 'dose2']

        self.output_data = pd.DataFrame(data=output_data, columns=column_names)
        replace_rows = self.output_data.idModality1[self.output_data.idModality1.isnull()].index.tolist()
        self.output_data.ix[replace_rows, 'idModality1'] = self.output_data.idModality2[replace_rows].values
        self.output_data.ix[replace_rows, 'idModality2'] = None
        self.output_data.ix[replace_rows, 'fluoroTime1'] = self.output_data.fluoroTime2[replace_rows].values
        self.output_data.ix[replace_rows, 'fluoroTime2'] = None
        self.output_data.ix[replace_rows, 'dose1'] = self.output_data.dose2[replace_rows].values
        self.output_data.ix[replace_rows, 'dose2'] = None

        self.output_data.operatorId.fillna(value='Ej angivet', inplace=True)
        # Remove rows with no fluoro time or fluoro dose values
        self.output_data = \
            self.output_data[self.output_data[['fluoroTime1', 'fluoroTime2', 'dose1', 'dose2']].sum(axis=1) > 0]

        replace_rows = self.output_data.fluoroTime1[self.output_data.fluoroTime1 == 0].index.tolist()
        if len(replace_rows) > 0:
            self.output_data.ix[replace_rows, 'fluoroTime1'] = None
        replace_rows = self.output_data.fluoroTime2[self.output_data.fluoroTime2 == 0].index.tolist()
        if len(replace_rows) > 0:
            self.output_data.ix[replace_rows, 'fluoroTime2'] = None
        replace_rows = self.output_data.dose1[self.output_data.dose1 == 0].index.tolist()
        if len(replace_rows) > 0:
            self.output_data.ix[replace_rows, 'dose1'] = None
        replace_rows = self.output_data.dose2[self.output_data.dose2 == 0].index.tolist()
        if len(replace_rows) > 0:
            self.output_data.ix[replace_rows, 'dose2'] = None
        self.output_data = self.output_data.drop_duplicates(keep='first')

    def assert_new_in_db(self):
        """ Go through the examinations and compare the new Orbit data to that in the ssp database. Remove examinations
        that are already in the database, match modalities, operators, and examination areas to what is found in the
        database.
        """
        # --------- #
        # Operators #
        # --------- #

        # Go through the operators and insert new operators into the db
        operators = DirtyOperator.objects.all().values('pk', 'dirty_name')
        operators = {obj['dirty_name']: obj['pk'] for obj in operators}
        new_operators = [i for i in np.unique(self.output_data.operatorId)
                         if i not in operators.keys()]
        self.log.debug(f'Found {len(new_operators)} new operators.')
        if len(new_operators) > 0:
            self.log.info('Inserting new operators into the database')
            for new_op in new_operators:
                operator = DirtyOperator(dirty_name=new_op)
                operator.save()
                # Add the new operator pk to the list of operators in the db
                operators[new_op] = operator.pk

        # Replace the operator name with the dirty operator id in the output_data data frame
        self.log.info('Replacing operator names in the orbit DataFrame with pk from the ssp db')
        for operator in np.unique([i for i in self.output_data.operatorId if i is not None]):
            self.output_data.operatorId.replace(operator, operators[operator], inplace=True)

        # ---------- #
        # Modalities #
        # ---------- #

        # Go through the modalities and insert new modalities into the db
        modalities = DirtyModality.objects.all().values('dirty_name', 'pk')
        modalities = {obj['dirty_name']: obj['pk'] for obj in modalities}
        new_modalities = [i for i in np.unique(
            [i for i in np.append(self.output_data.idModality1,self.output_data.idModality2) if i is not None]
        )if i not in modalities.keys()]
        self.log.debug(f'Found {len(new_modalities)} new modalities.')
        if len(new_modalities) > 0:
            self.log.info('Inserting new modalities into the database')
            for new_mod in new_modalities:
                modality = DirtyModality(dirty_name=new_mod)
                modality.save()
                # Add the new modality pk to the list of modalities in the db
                modalities[new_mod] = modality.pk

        # Replace the modality name with the dirty modality id in the output data frame
        self.log.info('Replacing modality names in the orbit DataFrame with pk from the ssp db')
        for modality in np.unique(
                [i for i in np.append(self.output_data.idModality1, self.output_data.idModality2) if i is not None]):
            self.output_data.idModality1.replace(modality, modalities[modality], inplace=True)
            self.output_data.idModality2.replace(modality, modalities[modality], inplace=True)

        # ------- #
        # Clinics #
        # ------- #

        # Go through the clinics and insert new clinics into the db
        clinics = DirtyClinic.objects.all().values('pk', 'dirty_name')
        clinics = {obj['dirty_name']: obj['pk'] for obj in clinics}
        new_clinics = [i for i in np.unique(self.output_data.clinicId) if i not in clinics.keys()]

        self.log.debug(f'Found {len(new_clinics)} new clinics')
        if len(new_clinics) > 0:
            self.log.info('Inserting new clinics into the database')
            for new_clinic in new_clinics:
                clinic = DirtyClinic(dirty_name=new_clinic)
                clinic.save()
                # Add the new operator pk to the list of operators in the db
                clinics[new_clinic] = clinic.pk

        # Replace the clinic name with the dirty clinic id in the output_data data frame
        self.log.info('Replacing clinic names in the orbit DataFrame with pk from the ssp db')
        for clinic in np.unique([i for i in self.output_data.clinicId if i is not None]):
            self.output_data.clinicId.replace(clinic, clinics[clinic], inplace=True)

        # ----------------- #
        # Exam Descriptions #
        # ----------------- #

        # Go through the exam descriptions and insert new descriptions into the db
        exam_descs = ExamDescription.objects.all().values('pk', 'description')
        exam_descs = {obj['description']: obj['pk'] for obj in exam_descs}
        new_descriptions = [i for i in np.unique(self.output_data.examDescId) if i not in exam_descs.keys()]

        self.log.debug(f'Found {len(new_descriptions)} new exam descriptions')
        if len(new_descriptions) > 0:
            self.log.info('Inserting new exam descriptions into the database')
            for new_desc in new_descriptions:
                desc = ExamDescription(description=new_desc)
                desc.save()
                exam_descs[new_desc] = desc.pk

        # Replace the exam description with the exam description id in the output_data data frame
        self.log.info('Replacing clinic names in the orbit DataFrame with pk from the ssp db')
        for description in np.unique([i for i in self.output_data.examDescId if i is not None]):
            self.output_data.examDescId.replace(description, exam_descs[description], inplace=True)

    def insert_into_sspdb(self):
        """ Insert the new data into the radiation protection portal database.
        """
        if len(self.output_data.examNo) < 1:
            return

        self.log.info(f'Checking for exams not already in the db')
        ssp_exam_numbers = Exam.objects.all().values('exam_no').distinct()
        ssp_exam_numbers = [obj['exam_no'] for obj in ssp_exam_numbers]

        # Filter out exams already in the databse
        self.output_data = self.output_data.query('examNo not in @ssp_exam_numbers')
        if len(self.output_data.examNo) < 1:
            return

        self.log.info(f'Inserting {len(self.output_data.examNo)} exams into the db')

        for row in self.output_data.itertuples():
            if not math.isnan(row.fluoroTime1) and row.fluoroTime1 is not None:
                query = Exam.objects.get_or_create(
                    exam_no=row.examNo,
                    exam_description=ExamDescription.objects.get(pk=row.examDescId),
                    exam_date=row.examDate,
                    dirty_clinic=DirtyClinic.objects.get(pk=row.clinicId),
                    dirty_operator=DirtyOperator.objects.get(pk=row.operatorId),
                    dirty_modality=DirtyModality.objects.get(pk=row.idModality1),
                    fluoro_time=(None if math.isnan(row.fluoroTime1) else row.fluoroTime1),
                    dose=(None if math.isnan(row.dose1) else row.dose1)
                )

            if not math.isnan(row.idModality2) and row.idModality2 is not None and not math.isnan(row.fluoroTime2) and row.fluoroTime2 is not None:
                query = Exam.objects.get_or_create(
                    exam_no=row.examNo,
                    exam_description=ExamDescription.objects.get(pk=row.examDescId),
                    exam_date=row.examDate,
                    dirty_clinic=DirtyClinic.objects.get(pk=row.clinicId),
                    dirty_operator=DirtyOperator.objects.get(pk=row.operatorId),
                    dirty_modality=DirtyModality.objects.get(pk=row.idModality2),
                    fluoro_time=(None if math.isnan(row.fluoroTime2) else row.fluoroTime2),
                    dose=(None if math.isnan(row.dose2) else row.dose2)
                )

        self.success = True
        self._save_success()

    def _save_success(self):
        """ Update the StartDate in the config file to the latest date in the insert2db data frame
        """
        Updates(updated=dt.datetime.now(), server=settings.FLUORO_TIME_DB_ENGINE['SERVER'], successful=self.success)
