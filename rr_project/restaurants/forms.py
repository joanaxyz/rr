from django import forms
from .models import Review, Restaurant

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 5, 'step': 0.1}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review...'})
        }

class RestaurantAddressForm(forms.ModelForm):
    """Form for editing restaurant address with separate components"""
    class Meta:
        model = Restaurant
        fields = ['city', 'street_block', 'street_name', 'street_number', 'postal_code']
        widgets = {
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'City',
                'required': True
            }),
            'street_block': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Block / District (Optional)',
            }),
            'street_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Street Name',
            }),
            'street_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Building / House Number',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Postal Code (Optional)',
            }),
        }

    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'contact_number']