# Generated by Django 4.2 on 2024-04-16 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nicurx_app', '0033_alter_medication_calculation_unit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medication',
            name='dose_limit',
            field=models.FloatField(default=1.0, help_text='Maximum dose'),
        ),
    ]
