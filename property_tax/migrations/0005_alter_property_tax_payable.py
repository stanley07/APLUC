# Generated by Django 5.0.1 on 2024-02-05 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_tax', '0004_alter_property_tax_payable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='tax_payable',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
    ]
