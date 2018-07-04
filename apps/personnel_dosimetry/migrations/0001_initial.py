# Generated by Django 2.0.5 on 2018-07-01 20:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clinic', models.TextField()),
                ('display_clinic', models.TextField(default=models.TextField())),
            ],
            options={
                'ordering': ('display_clinic',),
            },
        ),
        migrations.CreateModel(
            name='Deviation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('reported_to_authority', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DosimeterPlacement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dosimeter_placement', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Personnel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dosimetry_vendor_id', models.TextField(blank=True, null=True)),
                ('person_id', models.TextField(blank=True, null=True)),
                ('person_name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PersonnelDosimetryUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local_administrator', models.BooleanField(default=False)),
                ('personnel_dosimetry_admin', models.BooleanField(default=False)),
                ('inhouse_measurement_admin', models.BooleanField(default=False)),
                ('clinics', models.ManyToManyField(null=True, to='personnel_dosimetry.Clinic')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='PersonnelDosimetry', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
            },
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profession', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dosimetry_vendor', models.TextField(blank=True, null=True)),
                ('report', models.TextField(blank=True, null=True)),
                ('measurement_period_start', models.DateTimeField()),
                ('measurement_period_stop', models.DateTimeField()),
                ('hp10', models.FloatField(blank=True, null=True)),
                ('hp007', models.FloatField(blank=True, null=True)),
                ('hp10fn', models.FloatField(blank=True, null=True)),
                ('hp10tn', models.FloatField(blank=True, null=True)),
                ('other_measure', models.TextField(blank=True, null=True)),
                ('production', models.FloatField(blank=True, null=True)),
                ('production_isotope', models.TextField(blank=True, null=True)),
                ('yearly_production', models.FloatField(blank=True, null=True)),
                ('deviation', models.BooleanField(default=False)),
                ('spot_check', models.BooleanField(default=False)),
                ('area_measurement', models.BooleanField(default=False)),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personnel_dosimetry.Clinic')),
                ('personnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personnel_dosimetry.Personnel')),
            ],
        ),
        migrations.CreateModel(
            name='VendorDosimeterPlacement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor_dosimeter_placement', models.TextField()),
                ('dosimeter_placement', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='personnel_dosimetry.DosimeterPlacement')),
            ],
        ),
        migrations.AddField(
            model_name='result',
            name='vendor_dosimetry_placement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='personnel_dosimetry.VendorDosimeterPlacement'),
        ),
        migrations.AddField(
            model_name='personnel',
            name='profession',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='personnel_dosimetry.Profession'),
        ),
        migrations.AddField(
            model_name='deviation',
            name='result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deviant_result', to='personnel_dosimetry.Result'),
        ),
    ]
