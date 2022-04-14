# Generated by Django 3.2.9 on 2022-04-12 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20220406_1146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100)),
                ('note_parking', models.CharField(blank=True, max_length=200, null=True)),
                ('selected_parking_option', models.CharField(blank=True, max_length=200, null=True)),
                ('hotel_name', models.CharField(blank=True, max_length=200, null=True)),
                ('room_number', models.CharField(blank=True, max_length=20, null=True)),
                ('code', models.CharField(blank=True, max_length=20, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('city', models.CharField(max_length=100)),
                ('zip_code', models.CharField(blank=True, max_length=100, null=True)),
                ('address_type', models.CharField(choices=[('For appointment', 'For appointment'), ('For Valet', 'For Valet')], default='For appointment', max_length=100)),
                ('state', models.CharField(blank=True, max_length=127, null=True)),
                ('country', models.CharField(default='USA', max_length=127)),
                ('is_hotel', models.BooleanField(default=False)),
                ('apartment', models.CharField(blank=True, max_length=255, null=True)),
                ('gate_code', models.CharField(blank=True, max_length=255, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='address', to='users.client')),
            ],
            options={
                'verbose_name': "Client's address",
                'verbose_name_plural': "Clients' addresses",
            },
        ),
    ]