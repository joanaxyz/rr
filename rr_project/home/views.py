
from django.db.models import Avg, Count
from restaurants.models import Restaurant
from reservations.models import Reservation
from django.shortcuts import render

def home_view(request):
    """User home page"""
    user = request.user
    restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating', '-created_at')[:6]

    context = {
        'user': user,
        'reservations': Reservation.objects.filter(user=user) if hasattr(user, 'reservations') else [],
        'restaurants': restaurants,
    }
    return render(request, 'home/home.html', context)