# Generated by Django 4.2 on 2024-04-02 21:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nicurx_app', '0003_rename_portfolio_medicalrecord'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='major',
        ),
    ]
