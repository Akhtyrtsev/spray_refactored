# Generated by Django 3.2.9 on 2022-05-05 06:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('schedule', '0002_rename_break_hours_valetscheduleadditionaltime_additional_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='valetscheduleday',
            name='valet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='working_days', to='users.valet'),
        ),
    ]