# Generated by Django 4.2.6 on 2023-11-03 01:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GymApp', '0004_remove_userprofile_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='last_name',
        ),
    ]