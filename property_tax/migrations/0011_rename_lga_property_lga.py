# Generated by Django 5.0.1 on 2024-02-07 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('property_tax', '0010_alter_property_property_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='property',
            old_name='lga',
            new_name='LGA',
        ),
    ]