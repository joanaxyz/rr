from django import forms
from .models import OwnerVerificationRequest

class OwnerVerificationForm(forms.ModelForm):
    class Meta:
        model = OwnerVerificationRequest
        fields = [
            'govt_full_name',
            'government_id_type',
            'government_id_number',
            'business_address',
            'business_email',
            'tax_id',
            'business_license',
            'government_id_front',
            'government_id_back',
            'proof_of_ownership',
        ]
        widgets = {
            'govt_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'government_id_type': forms.TextInput(attrs={'class': 'form-control'}),
            'government_id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'business_address': forms.TextInput(attrs={'class': 'form-control'}),
            'business_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
