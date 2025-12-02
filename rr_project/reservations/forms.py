from .models import Reservation
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'guest_count', 'date', 'time', 'notes', 'table_numbers']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'guest_count': forms.Select(),
            'date': forms.DateInput(attrs={'type': 'date', 'min': str(date.today())}),
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
        
        # Set minimum date to today
        if 'date' in self.fields:
            self.fields['date'].widget.attrs['min'] = str(date.today())
    
    def clean_date(self):
        reservation_date = self.cleaned_data.get('date')
        if reservation_date:
            today = date.today()
            if reservation_date < today:
                raise ValidationError('Reservation date cannot be in the past. Please select today or a future date.')
            
            # Optional: Limit how far in advance reservations can be made (e.g., 1 year)
            max_future_date = today + timedelta(days=365)
            if reservation_date > max_future_date:
                raise ValidationError('Reservations can only be made up to 1 year in advance.')
        
        return reservation_date
    
    def clean(self):
        cleaned_data = super().clean()
        date_value = cleaned_data.get('date')
        time_value = cleaned_data.get('time')
        
        # If date is today, validate that time is not in the past
        if date_value == date.today() and time_value:
            now = timezone.now()
            reservation_datetime = timezone.make_aware(
                timezone.datetime.combine(date_value, time_value)
            )
            if reservation_datetime < now:
                raise ValidationError({
                    'time': 'Reservation time cannot be in the past. Please select a future time.'
                })
        
        return cleaned_data

