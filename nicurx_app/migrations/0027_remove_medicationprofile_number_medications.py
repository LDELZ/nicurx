# Generated by Django 4.2 on 2024-04-04 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nicurx_app', '0026_medicationprofile_number_medications'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicationprofile',
            name='number_medications',
        ),
    ]