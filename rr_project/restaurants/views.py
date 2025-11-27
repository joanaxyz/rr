from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count
from .models import Restaurant, Review, Cuisine, Tags
from .forms import RestaurantForm


# ================================
# OWNER DASHBOARD
# ================================
@login_required
def manage_dashboard(request):
    # Check if user is an owner
    if not hasattr(request.user, 'owner'):
        return redirect('home')

    # Get the first restaurant of this owner (if exists)
    restaurant = request.user.owner.restaurants.first()

    # Initialize dashboard stats
    if restaurant:
        total_reservations = restaurant.reservations.count() if hasattr(restaurant, 'reservations') else 0
        pending_reservations = restaurant.reservations.filter(status='pending').count() if hasattr(restaurant, 'reservations') else 0
        confirmed_reservations = restaurant.reservations.filter(status='confirmed').count() if hasattr(restaurant, 'reservations') else 0
        total_tables = restaurant.tables.count() if hasattr(restaurant, 'tables') else 0
    else:
        total_reservations = pending_reservations = confirmed_reservations = total_tables = 0

    context = {
        'restaurant': restaurant,
        'role': 'OWNER',
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'confirmed_reservations': confirmed_reservations,
        'total_tables': total_tables,
    }

    return render(request, 'manage_restaurant/dashboard.html', context)


# ================================
# CREATE RESTAURANT VIEW (OWNER)
# ================================
@login_required
def create_restaurant(request):
    # Make sure user is an owner
    if not hasattr(request.user, 'owner'):
        return redirect('home')

    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = request.user.owner
            restaurant.save()
            form.save_m2m()
            return redirect('restaurant_success')
    else:
        form = RestaurantForm()

    return render(request, 'manage_restaurant/create_restaurant.html', {'form': form})


# ================================
# OWNER - VIEW ALL RESTAURANTS
# ================================
@login_required
def view_restaurants(request):
    # Make sure user is an owner
    if not hasattr(request.user, 'owner'):
        return redirect('home')

    restaurants = request.user.owner.restaurants.all()

    context = {
        'restaurants': restaurants
    }
    return render(request, 'manage_restaurant/manage_restaurants.html', context)


# ================================
# RESTAURANT SUCCESS PAGE
# ================================
def restaurant_success(request):
    return render(request, 'restaurants/restaurant_success.html')


# ================================
# RESTAURANT DETAIL PAGE
# ================================
@login_required
def restaurant_detail_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    reviews = Review.objects.filter(restaurant=restaurant)
    recent_reviews = reviews.filter(created_at__gte=timezone.now() - timedelta(days=30))
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']

    context = {
        'restaurant': restaurant.to_dict(),
        'reviews': [r.to_dict() for r in reviews],
        'recent_reviews': [r.to_dict() for r in recent_reviews],
        'avg_rating': avg_rating,
        'review_form': None,
    }
    return render(request, 'restaurants/restaurant_detail.html', context)


# ================================
# ALL RESTAURANTS PAGE
# ================================
def restaurants_view(request):
    restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).prefetch_related('cuisines', 'tags')

    cuisines = Cuisine.objects.all().order_by('name')
    tags = Tags.objects.all().order_by('tag')

    restaurant_list = [r.to_dict() for r in restaurants]
    cuisines_list = [c.to_dict() for c in cuisines]
    tags_list = [t.to_dict() for t in tags]

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
        'cuisines': cuisines_list,
        'tags': tags_list,
        'day': day,
        'city': city,
        'guest_count': guest_count,
        'total_restaurants': len(restaurant_list),
    }
    return render(request, 'restaurants/restaurants.html', context)
