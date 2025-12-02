from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from datetime import datetime
from .models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count, Q
from datetime import timedelta
from django.utils import timezone
from .models import Cuisine, Tags
from .forms import ReviewForm
from accounts.models import Customer
from django.core.paginator import Paginator

# Create your views here.
def restaurant_detail_view(request, restaurant_id):
    """Restaurant detail page - supports both logged-in users and guests"""
    restaurant = get_object_or_404(
        Restaurant.objects.prefetch_related('cuisines', 'tags'),
        id=restaurant_id
    )
    reviews = Review.objects.filter(restaurant=restaurant).select_related('customer', 'customer__user')
    recent_reviews = reviews.filter(created_at__gte = timezone.now() - timedelta(days=30))
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    
    is_bookmarked = False
    existing_review = None
    customer = None
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            is_bookmarked = Bookmark.objects.filter(customer=customer, restaurant=restaurant).exists()
            # Check if customer has an existing review for this restaurant
            existing_review = Review.objects.filter(customer=customer, restaurant=restaurant).first()
        except Customer.DoesNotExist:
            pass
    
    review_form = None
    if request.method == 'POST' and 'submit_review' in request.POST:
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to leave a review.')
            return redirect('restaurants:detail', restaurant_id=restaurant_id)
        
        try:
            customer = Customer.objects.get(user=request.user)
            # Check if customer has an existing review
            existing_review = Review.objects.filter(customer=customer, restaurant=restaurant).first()
            
            if existing_review:
                # Update existing review
                review_form = ReviewForm(request.POST, instance=existing_review)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.customer = customer
                    review.restaurant = restaurant
                    review.save()
                    messages.success(request, 'Your review has been updated!')
                    return redirect('restaurants:detail', restaurant_id=restaurant_id)
                else:
                    messages.error(request, 'Please correct the errors in your review.')
            else:
                # Create new review
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.customer = customer
                    review.restaurant = restaurant
                    review.save()
                    messages.success(request, 'Thank you for your review!')
                    return redirect('restaurants:detail', restaurant_id=restaurant_id)
                else:
                    messages.error(request, 'Please correct the errors in your review.')
        except Customer.DoesNotExist:
            messages.error(request, 'You must be a customer to leave a review.')
    else:
        # Load existing review for editing if it exists, otherwise create new form
        if existing_review:
            review_form = ReviewForm(instance=existing_review)
        else:
            review_form = ReviewForm() if request.user.is_authenticated else None
    
    # Paginate reviews - only load reviews for current page
    paginator = Paginator(reviews.order_by('-created_at'), 10)  # 10 reviews per page
    page_number = request.GET.get('page', 1)
    reviews_page = paginator.get_page(page_number)
    
    # Only convert current page's reviews to dict
    reviews_list = list(reviews_page)
    reviews_dict = [r.to_dict() for r in reviews_list]
    
    # Recent reviews (limit to 5 most recent)
    recent_reviews = recent_reviews[:5]
    recent_reviews_dict = [r.to_dict() for r in recent_reviews]
    
    context = {
        'restaurant': restaurant,
        'restaurant_dict': restaurant.to_dict(),
        'reviews': reviews_list,
        'reviews_page': reviews_page,  # Pass page object for pagination
        'reviews_dict': reviews_dict,
        'recent_reviews': recent_reviews_dict,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'is_bookmarked': is_bookmarked,
        'existing_review': existing_review,
    }
    return render(request, 'restaurants/restaurant_detail.html', context)


@require_POST
def toggle_bookmark(request, restaurant_id):
    """Toggle bookmark for a restaurant - requires authentication"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Please log in to bookmark restaurants.',
            'requires_login': True
        }, status=401)
    
    try:
        customer = Customer.objects.get(user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        
        bookmark, created = Bookmark.objects.get_or_create(
            customer=customer,
            restaurant=restaurant
        )
        
        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True
            
        return JsonResponse({
            'success': True,
            'is_bookmarked': is_bookmarked
        })
    except Customer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'You must be a customer to bookmark restaurants.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def restaurants_view(request):
    # Start with base queryset
    restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).select_related('owner', 'owner__user').prefetch_related('cuisines', 'tags')
    
    # Apply filters from query parameters
    city = request.GET.get('city', '')
    guest_count = request.GET.get('guest_count', '')
    date = request.GET.get('date', '')
    search = request.GET.get('search', '')
    
    # Filter by city
    if city:
        restaurants = restaurants.filter(city__iexact=city)
    
    # Filter by guest count
    if guest_count:
        try:
            guest_num = int(guest_count)
            restaurants = restaurants.filter(max_guest_count__gte=guest_num)
        except ValueError:
            pass
    
    # Filter by operating day
    day = None
    if date:
        try:
            parsed_date = datetime.strptime(date, '%Y-%m-%d').date()
            weekday = parsed_date.weekday()
            weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            day = weekday_names[weekday]
            restaurants = restaurants.filter(operating_days__icontains=day)
        except ValueError:
            day = None
    
    # Search filter
    if search:
        restaurants = restaurants.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(city__icontains=search)
        )
    
    # Get filter options (cuisines and tags) - these are small, so loading all is fine
    cuisines = Cuisine.objects.all().order_by('name')
    tags = Tags.objects.all().order_by('tag')
    cuisines_list = [c.to_dict() for c in cuisines]
    tags_list = [t.to_dict() for t in tags]
    
    # Apply server-side pagination - only convert to dict the items on current page
    paginator = Paginator(restaurants.order_by('-avg_rating', '-created_at'), 12)  # 12 restaurants per page
    page_number = request.GET.get('page', 1)
    restaurants_page = paginator.get_page(page_number)
    
    # Pass both dict (for backward compatibility) and objects (for template access)
    restaurant_list = [r.to_dict() for r in restaurants_page]
    
    context = {
        'restaurants': restaurants_page,  # Pass page object with restaurant instances
        'restaurants_dict': restaurant_list,  # Keep dict for any JS that might need it
        'restaurants_page': restaurants_page,  # Pass page object for pagination controls
        'cuisines': cuisines_list,
        'tags': tags_list,
        'day': day,
        'city': city,
        'guest_count': guest_count,
        'date': date,
        'search': search,
        'total_restaurants': paginator.count,  # Total count from database
    }
    return render(request, 'restaurants/restaurants.html', context)
