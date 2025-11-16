from django import forms
from .models import OwnerVerificationRequest

class OwnerVerificationForm(forms.ModelForm):
    class Meta:
        model = OwnerVerificationRequest
        fields = [
            "gov_full_name",
            "id_type",
            "id_number",
            "business_address",
            "business_email",
            "proof_image",
        ]

        widgets = {
            "gov_full_name": forms.TextInput(attrs={"class": "form-control"}),
            "id_type": forms.TextInput(attrs={"class": "form-control"}),
            "id_number": forms.TextInput(attrs={"class": "form-control"}),
            "business_address": forms.TextInput(attrs={"class": "form-control"}),
            "business_email": forms.EmailInput(attrs={"class": "form-control"}),
        }
