from .models import Reservation
from django import forms

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'guest_count', 'date', 'time', 'notes', 'table_numbers']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'guest_count': forms.Select(),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any dietary restrictions, special occasions, or other requests...'}),
            'table_numbers': forms.HiddenInput(attrs={
                'id': 'table_num'
            })

        }
    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)  # expect restaurant to be passed
        super().__init__(*args, **kwargs)
        
        max_guests = restaurant.max_guest_count if restaurant else 10  # fallback if no restaurant
        self.fields['guest_count'].widget.choices = [(i, i) for i in range(1, max_guests + 1)]

