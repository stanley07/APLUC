from django import forms
from .models import Property, Payment


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'LGA',
            'property_address',
            'compound_size',
            'building_size',
            'category',
            'market_value',
            'depreciation_rate',
            'construction_value',
            'relief_rate',
            'charge_rate',
            'status',
            
        ]
        widgets = {
            'property_image': forms.FileInput(),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'property',  # Add this field
            'payment_option',  # Add this field
            'amount_paid',
            'installment_number',
            'remaining_balance',
        ]

    email = forms.EmailField(label='Email Address')

    def clean(self):
        cleaned_data = super().clean()
        # Add any additional validation logic here if needed
        return cleaned_data

class InstallmentPaymentForm(forms.Form):
    amount_per_installment = forms.DecimalField(label='Amount per Installment', min_value=0)
    number_of_installments = forms.IntegerField(label='Number of Installments', min_value=1)
    email = forms.EmailField(label='Email Address')