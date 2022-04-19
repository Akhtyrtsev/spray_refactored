# Generated by Django 3.2.9 on 2022-04-13 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(blank=True, choices=[('Los Angeles', 'Los Angeles'), ('Las Vegas', 'Las Vegas'), ('Miami', 'Miami')], max_length=128, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('subscription_type', models.CharField(blank=True, choices=[('Stay Golden', 'Stay Golden'), ('Sunkissed', 'Sunkissed')], max_length=256, null=True)),
                ('days', models.IntegerField(default=30)),
                ('appointments_left', models.IntegerField(default=0)),
            ],
        ),
    ]