# Generated by Django 4.2 on 2024-04-04 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nicurx_app', '0028_patient_discharge_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicationprofile',
            name='has_issues',
            field=models.BooleanField(default=False),
        ),
    ]