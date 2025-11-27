# manage_restaurant/forms.py
from django import forms
from restaurants.models import Restaurant, Cuisine

class RestaurantForm(forms.ModelForm):
    # optional: allow selecting multiple cuisines
    cuisines = forms.ModelMultipleChoiceField(
        queryset=Cuisine.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Restaurant
        fields = [
            'name',
            'street_number',
            'street_name',
            'street_block',
            'city',
            'postal_code',
            'email',
            'phone_number',
            'description',
            'image',
            'max_guest_count',
            'price_min',
            'price_max',
            'opening_time',
            'closing_time',
            'operating_days',
            'cuisines',  # include the M2M field
        ]
