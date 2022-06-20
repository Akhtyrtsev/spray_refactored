# Generated by Django 3.2.9 on 2022-06-20 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_valetfeed'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestToConfirmShift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('notes', models.CharField(max_length=255)),
                ('timezone', models.CharField(blank=True, choices=[('Los Angeles', 'Los Angeles'), ('Las Vegas', 'Las Vegas'), ('Miami', 'Miami')], max_length=32, null=True)),
                ('feed', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requests_to_confirm', to='feedback.valetfeed')),
            ],
            options={
                'verbose_name_plural': 'Valets: Close shift/appointment requests',
            },
        ),
    ]