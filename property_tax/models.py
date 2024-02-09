from django.db import models
from decimal import Decimal

class Property(models.Model):
    property_id = models.AutoField(primary_key=True)
    property_address = models.CharField(max_length=255, unique=True)
    market_value = models.DecimalField(max_digits=15, decimal_places=5)
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=5)
    building_size = models.DecimalField(max_digits=10, decimal_places=5)
    compound_size = models.DecimalField(max_digits=10, decimal_places=5)
    construction_value = models.IntegerField()
    LGA = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    relief_rate = models.DecimalField(max_digits=5, decimal_places=5)
    charge_rate = models.DecimalField(max_digits=5, decimal_places=5)
    tax_payable = models.DecimalField(max_digits=15, decimal_places=5)
    property_image = models.ImageField(upload_to='property_images/')
    status = models.CharField(max_length=255)

    def calculate_tax(self):
        # Calculate tax based on the provided formula
        self.tax_payable = (
            (self.compound_size * self.market_value + self.building_size * self.depreciation_rate) *
            self.relief_rate * self.charge_rate
        )

    def __str__(self):
        return self.property_address

class Payment(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=5)
    payment_date = models.DateTimeField(auto_now_add=True)
    installment_number = models.PositiveIntegerField(default=1)
    remaining_balance = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    payment_option = models.CharField(max_length=100, default='null')  # Add this field


    def __str__(self):
        # Define a string representation of the model instance
        return f"Payment for Property: {self.property}"


class Receipt(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=100, unique=True)
    issue_date = models.DateField(auto_now_add=True)

