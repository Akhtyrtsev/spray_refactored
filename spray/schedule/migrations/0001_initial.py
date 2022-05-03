# Generated by Django 3.2.9 on 2022-05-02 16:34

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import spray.utils.base_func


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ValetScheduleAdditionalTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('break_hours', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Valets: Additional working days',
            },
        ),
        migrations.CreateModel(
            name='ValetScheduleDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=32)),
                ('working_hours', django.contrib.postgres.fields.jsonb.JSONField(default=spray.utils.base_func.default_working_hours)),
                ('start_working_hours', models.TimeField(blank=True, null=True)),
                ('end_working_hours', models.TimeField(blank=True, null=True)),
                ('start_break_hours', models.TimeField(blank=True, null=True)),
                ('end_break_hours', models.TimeField(blank=True, null=True)),
                ('break_hours', django.contrib.postgres.fields.jsonb.JSONField(default=spray.utils.base_func.default_break_hours)),
                ('is_working', models.BooleanField(default=True)),
                ('is_required_to_work', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Valets: Working hours',
            },
        ),
        migrations.CreateModel(
            name='ValetScheduleOccupiedTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('break_hours', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Valets: day offs / breaks',
            },
        ),
    ]
