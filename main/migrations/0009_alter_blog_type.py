# Generated by Django 5.1.6 on 2025-02-28 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_blog_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
