# Generated by Django 3.2.9 on 2022-06-06 10:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import spray.users.managers


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0005_appointment_payout_ref'),
        ('schedule', '0002_delete_valetforschedule'),
        ('users', '0003_twillionumber'),
    ]

    operations = [
        migrations.CreateModel(
            name='ValetForSchedule',
            fields=[
            ],
            options={
                'verbose_name': 'Valet Schedule',
                'verbose_name_plural': 'Valets: Schedule',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.valet',),
            managers=[
                ('objects', spray.users.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ValetFeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_changed', models.DateTimeField(auto_now=True)),
                ('date_accepted', models.DateTimeField(blank=True, null=True)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
                ('visible', models.BooleanField(default=True)),
                ('type_of_request', models.CharField(choices=[('Re-assign', 'Re-assign'), ('NotOnCall', 'NotOnCall'), ('Changed', 'Changed'), ('Feed', 'Feed'), ('Automatic', 'Automatic')], default='FeedPost', max_length=255)),
                ('deleted', models.BooleanField(default=False)),
                ('timezone', models.CharField(blank=True, choices=[('Los Angeles', 'Los Angeles'), ('Las Vegas', 'Las Vegas'), ('Miami', 'Miami')], max_length=32, null=True)),
                ('additional_time_id', models.IntegerField(blank=True, null=True)),
                ('accepted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accepted_feeds', to=settings.AUTH_USER_MODEL)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feeds', to='appointments.appointment')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_feeds', to=settings.AUTH_USER_MODEL)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feeds', to=settings.AUTH_USER_MODEL)),
                ('shift', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.valetscheduleoccupiedtime')),
            ],
        ),
    ]