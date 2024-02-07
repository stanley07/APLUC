from django import forms
from .models import Property


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'lga',
            'property_address',
            'market_value',
            'depreciation_rate',
            'building_size',
            'compound_size',
            'construction_value',
            'relief_rate',
            'charge_rate',
            'category',
            'payment',
            'property_image',
        ]

        widgets = {
            'property_image': forms.FileInput(),
           
        }

class PaymentForm(forms.Form):
    # Define your form fields here
    amount = forms.DecimalField(label='Amount', min_value=0)
    email = forms.EmailField(label='Email Address')

    def clean(self):
        cleaned_data = super().clean()
        # Add any additional validation logic here if needed
        return cleaned_data
