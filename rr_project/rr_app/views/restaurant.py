
from django.contrib.auth.decorators import login_required

from ..models import Reservation, Restaurant, Review, Customer
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect, get_object_or_404
from ..forms.restaurant import  ReservationForm, ReviewForm
from django.contrib import messages
from django import forms
from django.db.models import Avg, Count
from datetime import datetime, timedelta
from django.utils import timezone
from ..models import Cuisine, Tags
from django.views.decorators.http import require_POST, require_GET
import json
from django.contrib.auth.decorators import login_required

# @login_required
def dashboard_view(request):
    """User dashboard"""
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
    return render(request, 'rr_app/restaurant/dashboard/dashboard.html', context)

@login_required
def reservation_management_view(request):
    """Manage user reservations"""
    reservations = Reservation.objects.filter(user=request.user).order_by('-date')
    
    if request.method == 'POST':
        # Handle reservation cancellation
        reservation_id = request.POST.get('cancel_reservation')
        if reservation_id:
            try:
                reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
                restaurant_name = reservation.restaurant.name
                reservation.delete()
                messages.success(request, f'Reservation at {restaurant_name} has been cancelled.')
            except Exception:
                messages.error(request, 'Failed to cancel reservation. Please try again.')
            return redirect('rr_app:reservation_management')
    
    context = {
        'reservations': reservations,
        'has_reservations': reservations.exists()
    }
    
    if not reservations.exists():
        messages.info(request, 'You have no reservations yet. Start by exploring restaurants and making your first reservation!')
    
    return render(request, 'rr_app/restaurant/reservation_management.html', context)


@login_required
def restaurant_detail_view(request, restaurant_id):
    """Restaurant detail page"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    reviews = Review.objects.filter(restaurant=restaurant)
    recent_reviews = reviews.filter(created_at__gte = timezone.now() - timedelta(days=30))
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    review_form = None
    
    reserve_form = None

    if request.method == 'POST':
        reserve_form = ReservationForm(request.POST, restaurant=restaurant)
        if reserve_form.is_valid():
            try:
                customer = Customer.objects.filter(user=request.user).first()
                reservation = reserve_form.save(commit=False)
                reservation.customer = customer
                reservation.restaurant = restaurant
                reservation.save()

                messages.success(request, f'You will receive an email once your reservation has been confirmed')
                return redirect('rr_app:restaurant_detail', restaurant_id=restaurant.id)
            except Exception as e:
                messages.error(request, f'An error occured during reservation: {str(e)}')
    else:
        reserve_form = ReservationForm(initial={
            'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email
        })


    context = {
        'restaurant': restaurant,
        'reviews': reviews,
        'recent_reviews': recent_reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'reserve_form': reserve_form,
    }
    return render(request, 'rr_app/restaurant/restaurant_detail.html', context)


def restaurants_view(request):
    restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).select_related().prefetch_related('cuisines', 'tags')
    
    # Get all cuisines and tags for filters
    cuisines = Cuisine.objects.all().order_by('name')
    tags = Tags.objects.all().order_by('tag')
    
    context = {
        'restaurants': restaurants,
        'cuisines': cuisines,
        'tags': tags,
    }
    return render(request, 'rr_app/restaurant/restaurants.html', context)

@login_required
def admin_restaurant_layout(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    context = {
        'restaurant': restaurant
    }
    return render(request, 'rr_app/restaurant/admin/adminlayout.html', context)


@login_required
@require_POST
def save_restaurant_layout(request, restaurant_id):
    """
    Save JSON layout sent by admin (AJAX POST).
    Expects JSON: { items: [ ... ] }
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    # Optional: check that request.user is allowed to edit (admin role) - you can add your permission logic here
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentication required")

    try:
        # request.body contains raw JSON; parse it
        payload = json.loads(request.body.decode('utf-8'))
        layout = payload.get('items', payload)  # accept {items: [...] } or raw [...]
        # Save into restaurant.layout
        restaurant.layout = layout
        restaurant.save(update_fields=['layout'])
        return JsonResponse({'success': True, 'message': 'Layout saved'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_GET
def load_restaurant_layout(request, restaurant_id):
    """
    Return the layout JSON for restaurant (used by the UI to load saved layout).
    """
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    layout = restaurant.layout or []
    return JsonResponse({'success': True, 'layout': layout})

def api_save_layout(request, restaurant_id):
    if request.method == 'POST':
        # Save the layout here
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'invalid method'}, status=400)

def api_load_layout(request, restaurant_id):
    # Load layout logic
    return JsonResponse({'layout': []})