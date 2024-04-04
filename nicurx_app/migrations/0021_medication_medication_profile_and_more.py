# Generated by Django 4.2 on 2024-04-04 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nicurx_app', '0020_remove_medication_medication_profile_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medication',
            name='medication_profile',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='medications', to='nicurx_app.medicationprofile'),
        ),
        migrations.AddField(
            model_name='patient',
            name='medication_profile',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='nicurx_app.medicationprofile'),
        ),
    ]