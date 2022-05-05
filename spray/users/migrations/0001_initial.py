# Generated by Django 3.2.9 on 2022-05-04 09:51

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import spray.users.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone', models.CharField(blank=True, max_length=17, null=True, validators=[django.core.validators.RegexValidator(message='Phone number must be all digits', regex='^\\d{10,15}$')])),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('user_type', models.PositiveSmallIntegerField(choices=[(1, 'superuser'), (2, 'staff'), (3, 'client'), (4, 'valet')], null=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('avatar_url', models.URLField(blank=True, null=True)),
                ('notification_sms', models.BooleanField(default=True)),
                ('notification_email', models.BooleanField(default=True)),
                ('notification_push', models.BooleanField(default=True)),
                ('rating', models.IntegerField(blank=True, null=True)),
                ('stripe_id', models.CharField(blank=True, max_length=30, null=True)),
                ('apple_id', models.CharField(blank=True, max_length=60, null=True)),
                ('docusign_envelope', models.CharField(blank=True, max_length=60, null=True)),
                ('is_phone_verified', models.BooleanField(default=False)),
                ('is_new', models.BooleanField(default=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', spray.users.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Groups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(blank=True, max_length=512, null=True)),
            ],
            options={
                'db_table': 'groups',
            },
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.user')),
                ('customer_status', models.CharField(blank=True, choices=[('New', 'New'), ('Returning', 'Returning'), ('Member', 'Member'), ('Subscriber', 'Subscriber')], max_length=100, null=True)),
                ('referal_code', models.CharField(blank=True, max_length=32, null=True)),
                ('notification_text_magic', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Users: Clients',
            },
            bases=('users.user',),
            managers=[
                ('objects', spray.users.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Valet',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.user')),
                ('valet_experience', models.TextField(blank=True, null=True)),
                ('valet_personal_phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='Personal phone')),
                ('notification_only_working_hours', models.BooleanField(default=False, help_text='valets field')),
                ('notification_shift', models.BooleanField(default=True, help_text='valets field')),
                ('notification_appointment', models.BooleanField(default=True, help_text='valets field')),
                ('valet_reaction_time', models.IntegerField(default=0, help_text='valets field')),
                ('valet_available_not_on_call', models.BooleanField(default=False, help_text='valets field')),
                ('city', models.CharField(blank=True, choices=[('Los Angeles', 'Los Angeles'), ('Las Vegas', 'Las Vegas'), ('Miami', 'Miami')], help_text='valets field', max_length=255, null=True)),
                ('feedback_popup_show_date', models.DateTimeField(blank=True, help_text='valets field', null=True)),
                ('emergency_name', models.CharField(blank=True, help_text='valets field', max_length=64, null=True)),
                ('license', models.CharField(blank=True, help_text='valets field', max_length=64, null=True)),
            ],
            options={
                'verbose_name': 'Valet',
                'verbose_name_plural': 'Users: Valets',
            },
            bases=('users.user',),
            managers=[
                ('objects', spray.users.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_string', models.CharField(blank=True, max_length=128, null=True)),
                ('note_parking', models.CharField(blank=True, max_length=256, null=True)),
                ('selected_parking_option', models.CharField(blank=True, max_length=200, null=True)),
                ('is_hotel', models.BooleanField(default=False)),
                ('hotel_name', models.CharField(blank=True, max_length=200, null=True)),
                ('room_number', models.CharField(blank=True, max_length=20, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('city', models.CharField(max_length=128)),
                ('zip_code', models.CharField(blank=True, max_length=128, null=True)),
                ('address_type', models.CharField(choices=[('Client', 'Client'), ('Valet', 'Valet')], default='Client', max_length=128)),
                ('state', models.CharField(blank=True, max_length=128, null=True)),
                ('country', models.CharField(default='USA', max_length=128)),
                ('apartment', models.CharField(blank=True, max_length=255, null=True)),
                ('gate_code', models.CharField(blank=True, max_length=255, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='address', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
            },
        ),
    ]