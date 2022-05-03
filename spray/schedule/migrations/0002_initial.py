# Generated by Django 3.2.9 on 2022-05-02 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='valetscheduleoccupiedtime',
            name='valet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='day_offs', to='users.valet'),
        ),
        migrations.AddField(
            model_name='valetscheduleday',
            name='valet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='working_days', to='users.valet'),
        ),
        migrations.AddField(
            model_name='valetscheduleadditionaltime',
            name='valet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='additional_days', to='users.valet'),
        ),
    ]
