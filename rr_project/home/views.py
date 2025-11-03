
from django.db.models import Avg, Count
from restaurants.models import Restaurant
from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode

def get_guest_ranges(max_guests):
    """Generate guest count ranges: 1-2, 3-4, 5-6, 7+"""
    if max_guests < 1:
        return []
    # Always use these standard ranges
    ranges = ["1-2", "3-4", "5-6"]
    if max_guests >= 7:
        ranges.append("7+")
    return ranges

def home_view(request):
    """User home page"""
    user = request.user
    restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating', '-created_at')[:6]

    restaurant_list = [r.to_dict() for r in restaurants]
    # Extract unique cities from all restaurants
    all_restaurants = Restaurant.objects.exclude(city__isnull=True).exclude(city__exact='')
    cities = sorted(set(all_restaurants.values_list('city', flat=True)))
    
    if request.method == 'POST':
        city = request.POST.get('city', '')
        guest_count = request.POST.get('guests', '')
        date = request.POST.get('date', '')
        
        query_params = urlencode({
            'city': city,
            'guest_count': guest_count,
            'date': date,
        })
        return redirect(f"{reverse('restaurants:restaurants')}?{query_params}")
    context = {
        'user': user,
        'restaurants': restaurant_list,
        'cities': cities
    }
    return render(request, 'home/home.html', context)