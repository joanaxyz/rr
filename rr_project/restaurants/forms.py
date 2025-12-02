from django import forms
from .models import Review, Restaurant

class ReviewForm(forms.ModelForm):
    rating = forms.DecimalField(
        max_value=5.0,
        min_value=0.0,
        widget=forms.NumberInput(attrs={
            'min': 0, 
            'max': 5, 
            'step': 0.5,
            'class': 'form-input',
            'style': 'width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;',
            'placeholder': 'Rating (0-5)'
        })
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4, 
            'placeholder': 'Write your review...',
            'class': 'form-input',
            'style': 'width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; resize: vertical;'
        })
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']

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