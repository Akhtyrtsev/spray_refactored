# Generated by Django 3.2.9 on 2022-05-04 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=30, null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('card_type', models.CharField(default='Visa', max_length=31)),
                ('last_4', models.CharField(default='0000', max_length=10)),
                ('expire_date', models.DateField(blank=True, null=True)),
                ('fingerprint', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
    ]
