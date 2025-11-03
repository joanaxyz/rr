from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from datetime import datetime
from .models import *
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import Avg, Count
from datetime import timedelta
from django.utils import timezone
from .models import Cuisine, Tags
from django.http import JsonResponse
from .forms import RestaurantAddressForm
import json

def get_guest_ranges(max_guests):
    """Generate guest count ranges: 1-2, 3-4, 5-6, 7+"""
    if max_guests < 1:
        return []
    # Always use these standard ranges
    ranges = ["1-2", "3-4", "5-6"]
    if max_guests >= 7:
        ranges.append("7+")
    return ranges

# Create your views here.
@login_required
def restaurant_detail_view(request, restaurant_id):
    """Restaurant detail page"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    reviews = Review.objects.filter(restaurant=restaurant)
    recent_reviews = reviews.filter(created_at__gte = timezone.now() - timedelta(days=30))
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    review_form = None

    context = {
        'restaurant': restaurant,
        'reviews': reviews,
        'recent_reviews': recent_reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
    }
    return render(request, 'restaurants/restaurant_detail.html', context)


def restaurants_view(request):
    restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).select_related().prefetch_related('cuisines', 'tags')
    
    # Get all cuisines and tags for filters
    cuisines = Cuisine.objects.all().order_by('name')
    tags = Tags.objects.all().order_by('tag')

    restaurant_list = [r.to_dict() for r in restaurants]

    city = request.GET.get('city', '')
    guest_count = request.GET.get('guest_count', '')
    date = request.GET.get('date', '')
    day = None 
    if date:
        try:
            parsed_date = datetime.strptime(date, '%Y-%m-%d').date()
            weekday = parsed_date.weekday()
            weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            day = weekday_names[weekday]
        except ValueError:
            day = None 
    
    context = {
        'restaurants': restaurant_list,
        'cuisines': cuisines,
        'tags': tags,
        'day': day,
        'city': city,
        'guest_count': guest_count,
    }
    return render(request, 'restaurants/restaurants.html', context)

@login_required
def update_restaurant_address(request, restaurant_id):
    """API endpoint to update restaurant address"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    try:
        data = json.loads(request.body)
        form = RestaurantAddressForm(data, instance=restaurant)
        
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Address updated successfully',
                'full_address': restaurant.full_address
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Form validation failed',
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
