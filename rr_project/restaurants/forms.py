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

class RestaurantForm(forms.ModelForm):
    """Main form for creating a restaurant"""
    class Meta:
        model = Restaurant
        fields = [
            'name',
            'description',
            'image',
            'opening_time',
            'closing_time',
            'max_guest_count',
            'price_min',
            'price_max',
            # Include the address fields directly
            'city',
            'street_block',
            'street_name',
            'street_number',
            'postal_code',
            'email',
            'phone_number',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Restaurant Name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Description'}),
            'image': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'Image URL'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'max_guest_count': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'price_min': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'price_max': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'street_block': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Block / District (Optional)'}),
            'street_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street Name'}),
            'street_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Building / House Number'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Postal Code (Optional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
        }
