# Generated by Django 5.1.6 on 2025-02-28 19:22

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_project_work_status_alter_project_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='type',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
    ]
