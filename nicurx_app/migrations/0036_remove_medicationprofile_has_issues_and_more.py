# Generated by Django 4.2 on 2024-04-17 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nicurx_app', '0035_medicationdosage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicationprofile',
            name='has_issues',
        ),
        migrations.AddField(
            model_name='medicationprofile',
            name='issues',
            field=models.IntegerField(default=False),
        ),
    ]
