# Generated by Django 3.2.9 on 2022-05-04 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('payment', '0002_payments_user'),
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientsubscription',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_subscriptions', to='users.client'),
        ),
        migrations.AddField(
            model_name='clientsubscription',
            name='payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to='payment.payments'),
        ),
        migrations.AddField(
            model_name='clientsubscription',
            name='subscription',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients', to='subscriptions.subscription'),
        ),
    ]