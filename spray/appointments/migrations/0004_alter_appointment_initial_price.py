# Generated by Django 3.2.9 on 2022-05-10 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_alter_appointment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='initial_price',
            field=models.FloatField(default=0, null=True),
        ),
    ]