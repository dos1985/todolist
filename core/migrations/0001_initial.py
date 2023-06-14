# Generated by Django 4.0.1 on 2023-06-14 08:46

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=20, region=None)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('role', models.CharField(choices=[('USR', 'user'), ('ADM', 'admin')], default='USR', max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
