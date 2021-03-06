# Generated by Django 3.2.9 on 2022-06-02 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_billingdetails_payout'),
        ('appointments', '0004_alter_appointment_initial_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='payout_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments', to='payment.payout'),
        ),
    ]
