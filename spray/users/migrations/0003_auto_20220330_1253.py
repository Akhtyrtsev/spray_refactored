# Generated by Django 3.2.9 on 2022-03-30 12:53

from django.db import migrations, models
import django.db.models.deletion
import spray.users.managers


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20220330_1247'),
    ]

    operations = [
        migrations.CreateModel(
            name='Valet',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.user')),
                ('test_valet', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('users.user',),
            managers=[
                ('objects', spray.users.managers.UserManager()),
            ],
        ),
        migrations.RenameField(
            model_name='client',
            old_name='test',
            new_name='test_client',
        ),
    ]
