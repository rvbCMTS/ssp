import os
import pyodbc
import sqlite3
from collections import namedtuple
import re
import pandas
from ..models import Machine, Protocol, Backup


def parse_db(input_directory: str):

    # find databases
    dbs = _find_db(input_directory)
    print(f'Hittade {len(dbs)} databaser i biblioteket')

    # for all databases
    if len(dbs) > 0:
        for db in dbs:
            print(db)

            # convert database from mdb to sqlite
            _mdb2sqlite(db)

            # parse temporary sqlite database
            [machine, df] = _parse_pex_db()

            # clean data before insert to new database
            df = _clean_df(df)

            # place dataframe in new database
            _prot2db(machine, df)

    print('klar')


def _find_db(input_directory: str) ->list:
    dbs = []
    for root, dirnames, filenames in os.walk(input_directory):
        for filename in filenames:
            if filename.lower().endswith('.mdb'):
                dbs.append(os.path.join(root, filename))
    return dbs

def _mdb2sqlite(mdb_database_path):

    # Open Access Database
    # Need to install driver for Access - Access Database Engine
    conn_str = (
        r'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};'
        r'DBQ={};'
        ).format(mdb_database_path)
    cnxn = pyodbc.connect(conn_str)

    # Need to change encoding to read the Access database - latin1 seams to work
    cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='latin1')
    cursor = cnxn.cursor()

    conn = sqlite3.connect('apps\\skeleton_protocols\\tools\\temp.sqlite3')
    c = conn.cursor()

    Table = namedtuple('Table', ['cat', 'schem', 'name', 'type'])

    # get a list of tables
    tables = []
    for row in cursor.tables():
        if row.table_type == 'TABLE':
            t = Table(row.table_cat, row.table_schem, row.table_name, row.table_type)
            tables.append(t)

    for t in tables:
        # print(t.name)

        # SQLite tables must being with a character or _
        t_name = t.name
        if not re.match('[a-zA-Z]', t.name):
            t_name = '_' + t_name

        # SQLite table names cannot contain space
        t_name = t_name.replace(" ", "_")

        # get table definition
        columns = []
        for row in cursor.columns(table=t.name):
            # print('    {} [{}({})]'.format(row.column_name, row.type_name, row.column_size))
            col_name = re.sub('[^a-zA-Z0-9]', '_', row.column_name)
            if col_name.upper() == 'DEFAULT':
                col_name = '{}{}'.format(col_name, t_name)
            # SQLite cannot have columns named INDEX
            if col_name.upper() == 'INDEX':
                col_name = 'Id'
            # Data type BIT -> TEXT
            if row.type_name == 'BIT':
                row.type_name = 'TEXT'

            # No need to specify size for column type
            # columns.append('{} {}({})'.format(col_name.capitalize(), row.type_name, row.column_size))
            columns.append('{} {}'.format(col_name.capitalize(), row.type_name))
        cols = ', '.join(columns)

        # create the table in SQLite
        c.execute('DROP TABLE IF EXISTS "{}"'.format(t_name))
        c.execute('CREATE TABLE "{}" ({})'.format(t_name, cols))

        # copy the data from MDB to SQLite
        cursor.execute('SELECT * FROM "{}"'.format(t.name))
        for row in cursor:
            values = []
            for value in row:
                if value is None:
                    values.append(u'NULL')
                else:
                    if isinstance(value, bytearray):
                        value = sqlite3.Binary(value)
                    else:
                        value = u'{}'.format(value)
                    values.append(value)
            v = ', '.join(['?'] * len(values))
            sql = 'INSERT INTO "{}" VALUES(' + v + ')'
            c.execute(sql.format(t_name), values)

    conn.commit()
    conn.close()

def _parse_pex_db():
    # Open temporary database
    conn = sqlite3.connect('apps\\skeleton_protocols\\tools\\temp.sqlite3')

    # Find which machine - query to db and conversion to dataframe
    fd = open('apps\\skeleton_protocols\\tools\\machine.sql', 'r')
    sql_machine = fd.read()
    fd.close()
    machine = pandas.read_sql_query(sql_machine, conn)

    # Find database version (grid parameter not in all database versions)
    sql_db_version = """SELECT * FROM GlobalVars """
    global_vars = pandas.read_sql_query(sql_db_version, conn)
    db_version = global_vars.loc[1, ['Varvalue']][0]

    # call correct sql-query
    if db_version == '60':
        fd = open('apps\\skeleton_protocols\\tools\\organ_programs_dbv60.sql', 'r')
        sql_organ_programs = fd.read()
        fd.close()
        # Read from db to dataframe
        df = pandas.read_sql_query(sql_organ_programs, conn)
    elif db_version == '45':
        fd = open('apps\\skeleton_protocols\\tools\\organ_programs_dbv45.sql', 'r')
        sql_organ_programs = fd.read()
        fd.close()
        # Read from db to dataframe
        df = pandas.read_sql_query(sql_organ_programs, conn)
        # Add None for grid
        df['grid'] = [float('nan')]*len(df)


    # Correcting kV och mAs
    df.kv = df.kv/10
    df.mas = df.mas/100

    # Replacing NaN with None
    df = df.where(pandas.notnull(df), None)

    # close database
    conn.close()

    return machine, df

def _clean_df(df):
    # Distinct Lut names

    lut_names = {
        '1':'01 Service Bone Black',
        '2':'02 Service Bone White',
        '3':'03 Low Contrast',
        '4':'04 Extremity/Skull',
        '4 Extremity/Skull': '04 Extremity/Skull',
        '5':'05 Chest',
        '6':'06 Extremity/Skull',
        '6 Extremity/Skull': '06 Extremity/Skull',
        '7':'07',
        '8':'08 Chest',
        '9':'09 Low Contrast',
        '10':'10 Abdomen/Ribs',
        '11':'11 Abdomen/Ribs',
        '12':'12 Extremity',
        '13':'13 Spine/Abdomen',
        '14':'14 Chest Mediastinum',
        '15':'15 Spine/Abdomen',
    }

    # Replace lut number with lut string
    for ind in lut_names:
        df.lut.replace(ind,lut_names[ind], inplace=True)

    return df

def _prot2db(machine, df):
    # date time for backup in UTC time
    tzdate = machine.last_modification[0]+'+02:00'

    # if exits (check only host_identifier), get entry, otherwise create it
    if Machine.objects.filter(host_identifier = machine.host_identifier[0]).exists():
        machine_entry = Machine.objects.get(host_identifier = machine.host_identifier[0])
    else:
        machine_entry = Machine.objects.create(hospital_name=machine.hospital_name[0],
                                               host_identifier=machine.host_identifier[0])


    # get or create backup entry
    backup_entry, backup_created = Backup.objects.get_or_create(machine=machine_entry,
                                                       datum=tzdate)
    if backup_created:
        for index, row in df.iterrows():
            # check if exists (all fields except datum), get it, otherwise create it.
            if Protocol.objects.filter(ris_name=row.ris_name,
                                      body_part=row.body_part,
                                      technique=row.technique,
                                      kv=row.kv,
                                      mas=row.mas,
                                      filter_cu=row.filter_cu,
                                      focus=row.focus,
                                      grid=row.grid,
                                      diamond_view=row.diamond_view,
                                      edge_filter_kernel_size=row.edge_filter_kernel_size,
                                      edge_filter_gain=row.edge_filter_gain,
                                      harmonization_kernel_size=row.harmonization_kernel_size,
                                      harmonization_gain=row.harmonization_gain,
                                      noise_reduction=row.noise_reduction,
                                      image_auto_amplification=row.image_auto_amplification,
                                      image_amplification_gain=row.image_amplification_gain,
                                      sensitivity=row.sensitivity,
                                      lut=row.lut,
                                      machine=machine_entry,
                                     ).exists():
                protocol_entry = Protocol.objects.get(ris_name=row.ris_name,
                                                      body_part=row.body_part,
                                                      technique=row.technique,
                                                      kv=row.kv,
                                                      mas=row.mas,
                                                      filter_cu=row.filter_cu,
                                                      focus=row.focus,
                                                      grid=row.grid,
                                                      diamond_view=row.diamond_view,
                                                      edge_filter_kernel_size=row.edge_filter_kernel_size,
                                                      edge_filter_gain=row.edge_filter_gain,
                                                      harmonization_kernel_size=row.harmonization_kernel_size,
                                                      harmonization_gain=row.harmonization_gain,
                                                      noise_reduction=row.noise_reduction,
                                                      image_auto_amplification=row.image_auto_amplification,
                                                      image_amplification_gain=row.image_amplification_gain,
                                                      sensitivity=row.sensitivity,
                                                      lut=row.lut,
                                                      machine=machine_entry,
                                                     )
            else:
                protocol_entry = Protocol.objects.create(ris_name=row.ris_name,
                                      body_part=row.body_part,
                                      technique=row.technique,
                                      kv=row.kv,
                                      mas=row.mas,
                                      filter_cu=row.filter_cu,
                                      focus=row.focus,
                                      grid=row.grid,
                                      diamond_view=row.diamond_view,
                                      edge_filter_kernel_size=row.edge_filter_kernel_size,
                                      edge_filter_gain=row.edge_filter_gain,
                                      harmonization_kernel_size=row.harmonization_kernel_size,
                                      harmonization_gain=row.harmonization_gain,
                                      noise_reduction=row.noise_reduction,
                                      image_auto_amplification=row.image_auto_amplification,
                                      image_amplification_gain=row.image_amplification_gain,
                                      sensitivity=row.sensitivity,
                                      lut=row.lut,
                                      datum = tzdate,
                                      machine=machine_entry,
                                      )

            # associate backup with protocol
            backup_entry.protocol.add(protocol_entry)







