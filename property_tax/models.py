# models.py
from django.db import models
from decimal import Decimal

class Property(models.Model):
    property_id = models.AutoField(primary_key=True)
    property_address = models.CharField(max_length=255, unique=True)  # Use unique=True to ensure uniqueness
    market_value = models.DecimalField(max_digits=15, decimal_places=5)
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=5)
    building_size = models.DecimalField(max_digits=10, decimal_places=5)
    compound_size = models.DecimalField(max_digits=10, decimal_places=5)
    construction_value = models.IntegerField()
    LGA = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    tax_payable = models.DecimalField(max_digits=15, decimal_places=5)
    payment = models.CharField(max_length=255)
    property_image = models.ImageField(upload_to='property_images/')
    relief_rate = models.DecimalField(max_digits=5, decimal_places=5)
    charge_rate = models.DecimalField(max_digits=5, decimal_places=5)

    def calculate_tax(self):
        # Calculate tax based on the provided formula
        self.tax_payable = (
            (self.compound_size * self.market_value + self.building_size * self.depreciation_rate) *
            self.relief_rate * self.charge_rate
        )

    def __str__(self):
        return self.property_address
