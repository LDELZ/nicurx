# Generated by Django 4.2 on 2024-04-04 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nicurx_app', '0023_remove_medicationprofile_high_risk_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicationprofile',
            name='id_number',
            field=models.IntegerField(null=True),
        ),
    ]
