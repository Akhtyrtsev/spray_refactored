# Generated by Django 3.2.9 on 2022-04-18 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payment', '0001_initial'),
        ('users', '0007_merge_0005_address_0006_auto_20220412_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(blank=True, choices=[('Los Angeles', 'Los Angeles'), ('Las Vegas', 'Las Vegas'), ('Miami', 'Miami')], max_length=100, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('subscription_type', models.CharField(blank=True, choices=[('Every 10 days', 'Every 10 days'), ('2x a month', '2x a month'), ('Weekly', 'Weekly'), ('Weekly Glow', 'Weekly Glow'), ('Bio Weekly Boost', 'Bio Weekly Boost'), ('Stay Golden', 'Stay Golden'), ('Sunkissed', 'Sunkissed'), ('Hidden', 'Hidden')], max_length=200, null=True)),
                ('save_percent', models.FloatField(default=0)),
                ('is_deprecated', models.BooleanField(default=False)),
                ('days', models.IntegerField(default=30)),
                ('appointments_left', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Subscription type/price',
                'verbose_name_plural': 'Subscriptions type/price',
            },
        ),
        migrations.CreateModel(
            name='ClientSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now_add=True)),
                ('cancellation_date', models.DateTimeField(blank=True, help_text='Once user cancels they have 2 months to use appointments', null=True)),
                ('appointments_left', models.IntegerField(default=0)),
                ('unused_appointments', models.IntegerField(default=0)),
                ('date_reminded', models.DateTimeField(auto_now_add=True)),
                ('extra_appointment', models.IntegerField(default=999)),
                ('days_to_update', models.IntegerField(default=30)),
                ('is_paused', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_referral_used', models.BooleanField(default=False)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_subscriptions', to='users.client')),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to='payment.payments')),
                ('subscription', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients', to='subscriptions.subscription')),
            ],
            options={
                'verbose_name': "Client's subscription",
                'verbose_name_plural': "Clients' subscriptions",
            },
        ),
    ]
