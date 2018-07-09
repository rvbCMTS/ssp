# Generated by Django 2.0.7 on 2018-07-09 07:16

from django.db import migrations


def insert_landauer_professions(apps, schema_editor):
    professions = [
        {'id': 1, 'profession': 'Servicepersonal'},
        {'id': 2, 'profession': 'Strålskyddspersonal'},
        {'id': 3, 'profession': 'Administratör'},
        {'id': 4, 'profession': 'Assistent'},
        {'id': 5, 'profession': 'Läkare'},
        {'id': 6, 'profession': 'Sköterska'},
        {'id': 7, 'profession': 'Framaceut'},
        {'id': 8, 'profession': 'Naturvetare'},
        {'id': 9, 'profession': 'Tekniker'},
        {'id': 10, 'profession': 'Sjukhusfysiker'},
        {'id': 11, 'profession': 'Tandläkare'},
        {'id': 12, 'profession': 'Veterinär'},
        {'id': 13, 'profession': 'Industripersonal'},
        {'id': 14, 'profession': 'Transportör'},
        {'id': 15, 'profession': 'Pilot'},
        {'id': 16, 'profession': 'Kabinpersonal'},
        {'id': 17, 'profession': 'Driftspersonal'},
        {'id': 18, 'profession': 'Mek reparatör'},
        {'id': 19, 'profession': 'Ställningsbyggare'},
        {'id': 20, 'profession': 'Isolerare'},
        {'id': 21, 'profession': 'Materialprovare'},
        {'id': 22, 'profession': 'Kemister'},
        {'id': 23, 'profession': 'Övrig kärnteknisk personal'},
        {'id': 24, 'profession': 'Undersköterska/-biträde'},
        {'id': 25, 'profession': 'Djursjukvårdare/-skötare'},
        {'id': 26, 'profession': 'Biomedicinsk analytiker'},
        {'id': 27, 'profession': 'Övrig personal'}
    ]

    Profession = apps.get_model('personnel_dosimetry', 'Profession')

    for profession in professions:
        p = Profession(landauer_profession_id=profession['id'], profession=profession['profession'])
        p.save()


class Migration(migrations.Migration):

    dependencies = [
        ('personnel_dosimetry', '0003_auto_20180709_0914'),
    ]

    operations = [
        migrations.RunPython(insert_landauer_professions)
    ]
