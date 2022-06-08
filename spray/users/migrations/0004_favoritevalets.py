# Generated by Django 3.2.9 on 2022-06-06 12:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_twillionumber'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteValets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred', models.BooleanField(blank=True, default=False, null=True)),
                ('only', models.BooleanField(blank=True, default=False, null=True)),
                ('favorite', models.BooleanField(blank=True, default=False, null=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_valets', to='users.client')),
                ('valet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients_who_liked', to='users.valet')),
            ],
        ),
    ]
