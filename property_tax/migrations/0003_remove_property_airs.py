# Generated by Django 5.0.1 on 2024-02-10 01:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('property_tax', '0002_rename_lga_property_lga_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='property',
            name='airs',
        ),
    ]