# Generated by Django 3.2.9 on 2022-04-21 12:20

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0003_auto_20220420_1442'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='clientsubscription',
            managers=[
                ('client_sub_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]