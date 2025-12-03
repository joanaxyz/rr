from .models import Reservation
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime, timedelta

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
        
        # Store restaurant for validation
        self.restaurant = restaurant
        
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
            
            # Check if restaurant is open on the selected date
            if self.restaurant:
                if not self.restaurant.is_open_on_date(reservation_date):
                    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    day_name = weekday_names[reservation_date.weekday()]
                    operating_days = self.restaurant.operating_days or 'Not specified'
                    raise ValidationError(
                        f'The restaurant is closed on {day_name}. '
                        f'Please select a date when the restaurant is open. Operating days: {operating_days}'
                    )
        
        return reservation_date
    
    def clean(self):
        cleaned_data = super().clean()
        date_value = cleaned_data.get('date')
        time_value = cleaned_data.get('time')
        
        if not date_value or not time_value:
            return cleaned_data
        
        # If date is today, validate that time is not in the past
        if date_value == date.today():
            now = timezone.now()
            reservation_datetime_naive = datetime.combine(date_value, time_value)
            reservation_datetime = timezone.make_aware(reservation_datetime_naive)
            
            if reservation_datetime < now:
                raise ValidationError({
                    'time': 'Reservation time cannot be in the past. Please select a future time.'
                })
        
        # Validate operating hours if restaurant is provided
        if self.restaurant and date_value and time_value:
            opening_time = self.restaurant.opening_time
            closing_time = self.restaurant.closing_time
            
            if not opening_time or not closing_time:
                # If operating hours are not set, skip validation
                return cleaned_data
            
            # Check if reservation time is within operating hours
            is_within_hours = False
            
            # Handle case where restaurant closes after midnight (e.g., opens 18:00, closes 02:00)
            if closing_time < opening_time:
                # Restaurant closes after midnight
                # Valid times are: opening_time <= time OR time <= closing_time
                is_within_hours = time_value >= opening_time or time_value <= closing_time
            else:
                # Normal case: opens and closes on same day
                is_within_hours = opening_time <= time_value <= closing_time
            
            if not is_within_hours:
                opening_str = opening_time.strftime('%I:%M %p')
                closing_str = closing_time.strftime('%I:%M %p')
                raise ValidationError({
                    'time': f'Reservation time must be within operating hours ({opening_str} - {closing_str}). '
                           f'Please select a time when the restaurant is open.'
                })
        
        return cleaned_data

