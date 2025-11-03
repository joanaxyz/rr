from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from datetime import datetime
from .models import *
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count
from datetime import timedelta
from django.utils import timezone
from .models import Cuisine, Tags
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
        'restaurant': restaurant.to_dict(),
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
