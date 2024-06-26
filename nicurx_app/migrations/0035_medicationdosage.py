# Generated by Django 4.2 on 2024-04-17 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nicurx_app', '0034_medication_dose_limit'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicationDosage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dose', models.FloatField(default=1.0, help_text='Dose')),
                ('medication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nicurx_app.medication')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nicurx_app.medicationprofile')),
            ],
        ),
    ]
