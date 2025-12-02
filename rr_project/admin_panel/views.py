from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
from django.http import HttpResponse
from accounts.models import User, Owner, Customer
from owner_verification.models import OwnerVerificationRequest
from restaurants.models import RestaurantCreationRequest, Restaurant, Cuisine, Tags, Review
from reservations.models import Reservation
from django.contrib.auth.hashers import make_password
from .decorators import admin_login_required
import csv
from datetime import datetime


@admin_login_required
def dashboard(request):
    pending_owner_requests = OwnerVerificationRequest.objects.filter(state='PENDING').count()
    pending_restaurant_requests = RestaurantCreationRequest.objects.filter(status='PENDING').count()
    total_admins = User.objects.filter(is_staff=True).count()
    total_users = User.objects.count()
    total_restaurants = Restaurant.objects.count()
    total_reservations = Reservation.objects.count()
    pending_reservations = Reservation.objects.filter(status='PENDING').count()
    total_reviews = Review.objects.count()
    avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'pending_owner_requests': pending_owner_requests,
        'pending_restaurant_requests': pending_restaurant_requests,
        'total_admins': total_admins,
        'total_users': total_users,
        'total_restaurants': total_restaurants,
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 2),
        'pending_owner_count': pending_owner_requests,
        'pending_restaurant_count': pending_restaurant_requests,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@admin_login_required
def manage_admins(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        if action == 'add':
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                if not user.is_staff:
                    user.is_staff = True
                    user.save()
                    messages.success(request, f'{user.email} has been made an admin.')
                else:
                    messages.info(request, f'{user.email} is already an admin.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
        
        elif action == 'remove' and user_id:
            user = get_object_or_404(User, id=user_id)
            if user.id != request.user.id:
                user.is_staff = False
                user.save()
                messages.success(request, f'{user.email} has been removed from admins.')
            else:
                messages.error(request, 'You cannot remove yourself as an admin.')
        
        return redirect('admin_panel:manage_admins')
    
    admins = User.objects.filter(is_staff=True)
    non_admins = User.objects.filter(is_staff=False)
    
    context = {
        'admins': admins,
        'non_admins': non_admins,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/manage_admins.html', context)

@admin_login_required
def owner_verification_requests(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        request_id = request.POST.get('request_id')
        verification_request = get_object_or_404(OwnerVerificationRequest, id=request_id)
        
        if action == 'accept':
            verification_request.state = 'ACCEPTED'
            verification_request.save()
            
            user = verification_request.user
            user.role = 'OWNER'
            user.save()
            
            Owner.objects.get_or_create(user=user)
            
            messages.success(request, f'Owner verification for {user.email} has been accepted.')
        
        elif action == 'reject':
            verification_request.state = 'NOT_APPROVED'
            verification_request.save()
            messages.info(request, f'Owner verification for {verification_request.user.email} has been rejected.')
        
        return redirect('admin_panel:owner_verification_requests')
    
    pending_requests = OwnerVerificationRequest.objects.filter(state='PENDING').order_by('-created_at')
    accepted_requests = OwnerVerificationRequest.objects.filter(state='ACCEPTED').order_by('-updated_at')[:10]
    rejected_requests = OwnerVerificationRequest.objects.filter(state='NOT_APPROVED').order_by('-updated_at')[:10]
    
    context = {
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
        'rejected_requests': rejected_requests,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/owner_verification_requests.html', context)

@admin_login_required
def restaurant_creation_requests(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        request_id = request.POST.get('request_id')
        creation_request = get_object_or_404(RestaurantCreationRequest, id=request_id)
        
        if action == 'accept':
            try:
                owner = Owner.objects.get(user=creation_request.user)
            except Owner.DoesNotExist:
                messages.error(request, f'User {creation_request.user.email} is not an owner. Please verify them as owner first.')
                return redirect('admin_panel:restaurant_creation_requests')
            
            restaurant = Restaurant.objects.create(
                name=creation_request.name,
                email=creation_request.email,
                phone_number=creation_request.phone_number,
                description=creation_request.description,
                street_number=creation_request.street_number,
                street_name=creation_request.street_name,
                street_block=creation_request.street_block,
                city=creation_request.city,
                postal_code=creation_request.postal_code,
                price_min=creation_request.price_min,
                price_max=creation_request.price_max,
                max_guest_count=creation_request.max_guest_count,
                opening_time=creation_request.opening_time,
                closing_time=creation_request.closing_time,
                operating_days=creation_request.operating_days,
                image=creation_request.image,
                owner=owner
            )
            
            creation_request.status = 'ACCEPTED'
            creation_request.save()
            
            messages.success(request, f'Restaurant "{restaurant.name}" has been created successfully.')
        
        elif action == 'reject':
            creation_request.status = 'REJECTED'
            creation_request.save()
            messages.info(request, f'Restaurant creation request for "{creation_request.name}" has been rejected.')
        
        return redirect('admin_panel:restaurant_creation_requests')
    
    pending_requests = RestaurantCreationRequest.objects.filter(status='PENDING').order_by('-created_at')
    accepted_requests = RestaurantCreationRequest.objects.filter(status='ACCEPTED').order_by('-updated_at')[:10]
    rejected_requests = RestaurantCreationRequest.objects.filter(status='REJECTED').order_by('-updated_at')[:10]
    
    context = {
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
        'rejected_requests': rejected_requests,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/restaurant_creation_requests.html', context)

# User Management CRUD
@admin_login_required
def users(request):
    search = request.GET.get('search', '')
    role = request.GET.get('role', '')
    users_list = User.objects.all()
    
    if search:
        users_list = users_list.filter(
            Q(email__icontains=search) | 
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if role:
        users_list = users_list.filter(role=role)
    
    paginator = Paginator(users_list.order_by('-date_joined'), 25)
    page = request.GET.get('page')
    users_page = paginator.get_page(page)
    
    context = {
        'users': users_page,
        'search': search,
        'role': role,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/users.html', context)

@admin_login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {
        'user_obj': user,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/user_detail.html', context)

@admin_login_required
def user_create(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', 'CUSTOMER')
        phone_number = request.POST.get('phone_number', '')
        is_staff_user = request.POST.get('is_staff') == 'on'
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'User with this email already exists.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'User with this username already exists.')
        else:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                phone_number=phone_number,
                is_staff=is_staff_user
            )
            messages.success(request, f'User {user.email} created successfully.')
            return redirect('admin_panel:user_detail', user_id=user.id)
    
    context = {
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/user_form.html', context)

@admin_login_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.role = request.POST.get('role', 'CUSTOMER')
        user.phone_number = request.POST.get('phone_number', '')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.banned = request.POST.get('banned') == 'on'
        
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        messages.success(request, f'User {user.email} updated successfully.')
        return redirect('admin_panel:user_detail', user_id=user.id)
    
    context = {
        'user_obj': user,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/user_form.html', context)

@admin_login_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        email = user.email
        user.delete()
        messages.success(request, f'User {email} deleted successfully.')
        return redirect('admin_panel:users')
    return redirect('admin_panel:user_detail', user_id=user_id)

# Restaurant Management CRUD
@admin_login_required
def restaurants(request):
    search = request.GET.get('search', '')
    restaurants_list = Restaurant.objects.all()
    
    if search:
        restaurants_list = restaurants_list.filter(
            Q(name__icontains=search) |
            Q(city__icontains=search) |
            Q(email__icontains=search)
        )
    
    paginator = Paginator(restaurants_list.order_by('-created_at'), 25)
    page = request.GET.get('page')
    restaurants_page = paginator.get_page(page)
    
    context = {
        'restaurants': restaurants_page,
        'search': search,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/restaurants.html', context)

@admin_login_required
def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    context = {
        'restaurant': restaurant,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/restaurant_detail.html', context)

@admin_login_required
def restaurant_create(request):
    owners = Owner.objects.all()
    
    if request.method == 'POST':
        try:
            owner_id = request.POST.get('owner')
            owner = Owner.objects.get(id=owner_id) if owner_id else None
            
            restaurant = Restaurant.objects.create(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                phone_number=request.POST.get('phone_number'),
                description=request.POST.get('description', ''),
                street_number=request.POST.get('street_number', ''),
                street_name=request.POST.get('street_name', ''),
                street_block=request.POST.get('street_block', ''),
                city=request.POST.get('city', ''),
                postal_code=request.POST.get('postal_code', ''),
                price_min=request.POST.get('price_min') or 0,
                price_max=request.POST.get('price_max') or 0,
                max_guest_count=request.POST.get('max_guest_count') or 0,
                opening_time=request.POST.get('opening_time') or None,
                closing_time=request.POST.get('closing_time') or None,
                operating_days=request.POST.get('operating_days', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun'),
                image=request.POST.get('image', ''),
                owner=owner
            )
            messages.success(request, f'Restaurant "{restaurant.name}" created successfully.')
            return redirect('admin_panel:restaurant_detail', restaurant_id=restaurant.id)
        except Exception as e:
            messages.error(request, f'Error creating restaurant: {str(e)}')
    
    context = {
        'owners': owners,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/restaurant_form.html', context)

@admin_login_required
def restaurant_edit(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    owners = Owner.objects.all()
    
    if request.method == 'POST':
        try:
            owner_id = request.POST.get('owner')
            restaurant.owner = Owner.objects.get(id=owner_id) if owner_id else None
            restaurant.name = request.POST.get('name')
            restaurant.email = request.POST.get('email')
            restaurant.phone_number = request.POST.get('phone_number')
            restaurant.description = request.POST.get('description', '')
            restaurant.street_number = request.POST.get('street_number', '')
            restaurant.street_name = request.POST.get('street_name', '')
            restaurant.street_block = request.POST.get('street_block', '')
            restaurant.city = request.POST.get('city', '')
            restaurant.postal_code = request.POST.get('postal_code', '')
            restaurant.price_min = request.POST.get('price_min') or 0
            restaurant.price_max = request.POST.get('price_max') or 0
            restaurant.max_guest_count = request.POST.get('max_guest_count') or 0
            restaurant.opening_time = request.POST.get('opening_time') or None
            restaurant.closing_time = request.POST.get('closing_time') or None
            restaurant.operating_days = request.POST.get('operating_days', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun')
            if request.POST.get('image'):
                restaurant.image = request.POST.get('image')
            restaurant.save()
            messages.success(request, f'Restaurant "{restaurant.name}" updated successfully.')
            return redirect('admin_panel:restaurant_detail', restaurant_id=restaurant.id)
        except Exception as e:
            messages.error(request, f'Error updating restaurant: {str(e)}')
    
    context = {
        'restaurant': restaurant,
        'owners': owners,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/restaurant_form.html', context)

@admin_login_required
def restaurant_delete(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        name = restaurant.name
        restaurant.delete()
        messages.success(request, f'Restaurant "{name}" deleted successfully.')
        return redirect('admin_panel:restaurants')
    return redirect('admin_panel:restaurant_detail', restaurant_id=restaurant_id)

# Reservation Management CRUD
@admin_login_required
def reservations(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    reservations_list = Reservation.objects.all()
    
    if search:
        reservations_list = reservations_list.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(restaurant__name__icontains=search)
        )
    
    if status:
        reservations_list = reservations_list.filter(status=status)
    
    paginator = Paginator(reservations_list.order_by('-created_at'), 25)
    page = request.GET.get('page')
    reservations_page = paginator.get_page(page)
    
    context = {
        'reservations': reservations_page,
        'search': search,
        'status': status,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/reservations.html', context)

@admin_login_required
def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    context = {
        'reservation': reservation,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/reservation_detail.html', context)

@admin_login_required
def reservation_create(request):
    restaurants = Restaurant.objects.all()
    customers = Customer.objects.all()
    
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')
            customer = Customer.objects.get(id=customer_id) if customer_id else None
            restaurant_id = request.POST.get('restaurant')
            restaurant = Restaurant.objects.get(id=restaurant_id) if restaurant_id else None
            
            reservation = Reservation.objects.create(
                customer=customer,
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                guest_count=request.POST.get('guest_count') or 0,
                date=request.POST.get('date'),
                time=request.POST.get('time'),
                notes=request.POST.get('notes', ''),
                status=request.POST.get('status', 'PENDING'),
                restaurant=restaurant
            )
            messages.success(request, f'Reservation created successfully.')
            return redirect('admin_panel:reservation_detail', reservation_id=reservation.id)
        except Exception as e:
            messages.error(request, f'Error creating reservation: {str(e)}')
    
    context = {
        'restaurants': restaurants,
        'customers': customers,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/reservation_form.html', context)

@admin_login_required
def reservation_edit(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    restaurants = Restaurant.objects.all()
    customers = Customer.objects.all()
    
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')
            reservation.customer = Customer.objects.get(id=customer_id) if customer_id else None
            restaurant_id = request.POST.get('restaurant')
            reservation.restaurant = Restaurant.objects.get(id=restaurant_id) if restaurant_id else None
            reservation.name = request.POST.get('name')
            reservation.email = request.POST.get('email')
            reservation.guest_count = request.POST.get('guest_count') or 0
            reservation.date = request.POST.get('date')
            reservation.time = request.POST.get('time')
            reservation.notes = request.POST.get('notes', '')
            reservation.status = request.POST.get('status', 'PENDING')
            reservation.save()
            messages.success(request, f'Reservation updated successfully.')
            return redirect('admin_panel:reservation_detail', reservation_id=reservation.id)
        except Exception as e:
            messages.error(request, f'Error updating reservation: {str(e)}')
    
    context = {
        'reservation': reservation,
        'restaurants': restaurants,
        'customers': customers,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/reservation_form.html', context)

@admin_login_required
def reservation_delete(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, 'Reservation deleted successfully.')
        return redirect('admin_panel:reservations')
    return redirect('admin_panel:reservation_detail', reservation_id=reservation_id)

# Review Management CRUD
@admin_login_required
def reviews(request):
    search = request.GET.get('search', '')
    reviews_list = Review.objects.all()
    
    if search:
        reviews_list = reviews_list.filter(
            Q(restaurant__name__icontains=search) |
            Q(comment__icontains=search) |
            Q(customer__user__email__icontains=search)
        )
    
    paginator = Paginator(reviews_list.order_by('-created_at'), 25)
    page = request.GET.get('page')
    reviews_page = paginator.get_page(page)
    
    context = {
        'reviews': reviews_page,
        'search': search,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/reviews.html', context)

@admin_login_required
def review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    context = {
        'review': review,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/review_detail.html', context)

@admin_login_required
def review_create(request):
    restaurants = Restaurant.objects.all()
    customers = Customer.objects.all()
    
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')
            customer = Customer.objects.get(id=customer_id) if customer_id else None
            restaurant_id = request.POST.get('restaurant')
            restaurant = Restaurant.objects.get(id=restaurant_id) if restaurant_id else None
            
            review = Review.objects.create(
                customer=customer,
                restaurant=restaurant,
                rating=request.POST.get('rating') or 0,
                comment=request.POST.get('comment', '')
            )
            messages.success(request, 'Review created successfully.')
            return redirect('admin_panel:review_detail', review_id=review.id)
        except Exception as e:
            messages.error(request, f'Error creating review: {str(e)}')
    
    context = {
        'restaurants': restaurants,
        'customers': customers,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/review_form.html', context)

@admin_login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    restaurants = Restaurant.objects.all()
    customers = Customer.objects.all()
    
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')
            review.customer = Customer.objects.get(id=customer_id) if customer_id else None
            restaurant_id = request.POST.get('restaurant')
            review.restaurant = Restaurant.objects.get(id=restaurant_id) if restaurant_id else None
            review.rating = request.POST.get('rating') or 0
            review.comment = request.POST.get('comment', '')
            review.save()
            messages.success(request, 'Review updated successfully.')
            return redirect('admin_panel:review_detail', review_id=review.id)
        except Exception as e:
            messages.error(request, f'Error updating review: {str(e)}')
    
    context = {
        'review': review,
        'restaurants': restaurants,
        'customers': customers,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/review_form.html', context)

@admin_login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully.')
        return redirect('admin_panel:reviews')
    return redirect('admin_panel:review_detail', review_id=review_id)

# Cuisine Management CRUD
@admin_login_required
def cuisines(request):
    search = request.GET.get('search', '')
    cuisines_list = Cuisine.objects.all()
    
    if search:
        cuisines_list = cuisines_list.filter(name__icontains=search)
    
    paginator = Paginator(cuisines_list.order_by('name'), 25)
    page = request.GET.get('page')
    cuisines_page = paginator.get_page(page)
    
    context = {
        'cuisines': cuisines_page,
        'search': search,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/cuisines.html', context)

@admin_login_required
def cuisine_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if Cuisine.objects.filter(name=name).exists():
            messages.error(request, 'Cuisine with this name already exists.')
        else:
            cuisine = Cuisine.objects.create(name=name)
            messages.success(request, f'Cuisine "{cuisine.name}" created successfully.')
            return redirect('admin_panel:cuisines')
    
    context = {
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/cuisine_form.html', context)

@admin_login_required
def cuisine_edit(request, cuisine_id):
    cuisine = get_object_or_404(Cuisine, id=cuisine_id)
    
    if request.method == 'POST':
        cuisine.name = request.POST.get('name')
        cuisine.save()
        messages.success(request, f'Cuisine "{cuisine.name}" updated successfully.')
        return redirect('admin_panel:cuisines')
    
    context = {
        'cuisine': cuisine,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/cuisine_form.html', context)

@admin_login_required
def cuisine_delete(request, cuisine_id):
    cuisine = get_object_or_404(Cuisine, id=cuisine_id)
    if request.method == 'POST':
        name = cuisine.name
        cuisine.delete()
        messages.success(request, f'Cuisine "{name}" deleted successfully.')
        return redirect('admin_panel:cuisines')
    return redirect('admin_panel:cuisines')

# Tag Management CRUD
@admin_login_required
def tags(request):
    search = request.GET.get('search', '')
    tags_list = Tags.objects.all()
    
    if search:
        tags_list = tags_list.filter(tag__icontains=search)
    
    paginator = Paginator(tags_list.order_by('tag'), 25)
    page = request.GET.get('page')
    tags_page = paginator.get_page(page)
    
    context = {
        'tags': tags_page,
        'search': search,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/tags.html', context)

@admin_login_required
def tag_create(request):
    if request.method == 'POST':
        tag = request.POST.get('tag')
        if Tags.objects.filter(tag=tag).exists():
            messages.error(request, 'Tag with this name already exists.')
        else:
            tag_obj = Tags.objects.create(tag=tag)
            messages.success(request, f'Tag "{tag_obj.tag}" created successfully.')
            return redirect('admin_panel:tags')
    
    context = {
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/tag_form.html', context)

@admin_login_required
def tag_edit(request, tag_id):
    tag = get_object_or_404(Tags, id=tag_id)
    
    if request.method == 'POST':
        tag.tag = request.POST.get('tag')
        tag.save()
        messages.success(request, f'Tag "{tag.tag}" updated successfully.')
        return redirect('admin_panel:tags')
    
    context = {
        'tag': tag,
        'pending_owner_count': OwnerVerificationRequest.objects.filter(state='PENDING').count(),
        'pending_restaurant_count': RestaurantCreationRequest.objects.filter(status='PENDING').count(),
    }
    return render(request, 'admin_panel/tag_form.html', context)

@admin_login_required
def tag_delete(request, tag_id):
    tag = get_object_or_404(Tags, id=tag_id)
    if request.method == 'POST':
        tag_name = tag.tag
        tag.delete()
        messages.success(request, f'Tag "{tag_name}" deleted successfully.')
        return redirect('admin_panel:tags')
    return redirect('admin_panel:tags')

# CSV Export Functions
@admin_login_required
def export_users_csv(request):
    search = request.GET.get('search', '')
    role = request.GET.get('role', '')
    users_list = User.objects.all()
    
    if search:
        users_list = users_list.filter(
            Q(email__icontains=search) | 
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    if role:
        users_list = users_list.filter(role=role)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Email', 'Username', 'First Name', 'Last Name', 'Full Name', 'Role', 'Phone Number', 'Is Staff', 'Is Active', 'Banned', 'Date Joined'])
    
    for user in users_list.order_by('-date_joined'):
        writer.writerow([
            user.email,
            user.username,
            user.first_name or '',
            user.last_name or '',
            user.get_full_name() or '',
            user.get_role_display(),
            user.phone_number or '',
            'Yes' if user.is_staff else 'No',
            'Yes' if user.is_active else 'No',
            'Yes' if user.banned else 'No',
            user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else ''
        ])
    
    return response

@admin_login_required
def export_restaurants_csv(request):
    search = request.GET.get('search', '')
    restaurants_list = Restaurant.objects.all()
    
    if search:
        restaurants_list = restaurants_list.filter(
            Q(name__icontains=search) |
            Q(city__icontains=search) |
            Q(email__icontains=search)
        )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="restaurants_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Owner Email', 'Email', 'Phone Number', 'City', 'Street Address', 'Postal Code', 'Price Min', 'Price Max', 'Max Guest Count', 'Opening Time', 'Closing Time', 'Operating Days', 'Created At'])
    
    for restaurant in restaurants_list.order_by('-created_at'):
        street_address = f"{restaurant.street_number or ''} {restaurant.street_name or ''} {restaurant.street_block or ''}".strip()
        writer.writerow([
            restaurant.name,
            restaurant.owner.user.email if restaurant.owner else '',
            restaurant.email or '',
            restaurant.phone_number or '',
            restaurant.city or '',
            street_address,
            restaurant.postal_code or '',
            restaurant.price_min or 0,
            restaurant.price_max or 0,
            restaurant.max_guest_count or 0,
            restaurant.opening_time.strftime('%H:%M:%S') if restaurant.opening_time else '',
            restaurant.closing_time.strftime('%H:%M:%S') if restaurant.closing_time else '',
            restaurant.operating_days or '',
            restaurant.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(restaurant, 'created_at') and restaurant.created_at else ''
        ])
    
    return response

@admin_login_required
def export_reservations_csv(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    reservations_list = Reservation.objects.all()
    
    if search:
        reservations_list = reservations_list.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(restaurant__name__icontains=search)
        )
    
    if status:
        reservations_list = reservations_list.filter(status=status)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reservations_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Guest Name', 'Email', 'Restaurant', 'Date', 'Time', 'Guest Count', 'Status', 'Notes', 'Customer Email', 'Created At'])
    
    for reservation in reservations_list.order_by('-created_at'):
        writer.writerow([
            reservation.name,
            reservation.email,
            reservation.restaurant.name if reservation.restaurant else '',
            reservation.date.strftime('%Y-%m-%d') if reservation.date else '',
            reservation.time.strftime('%H:%M:%S') if reservation.time else '',
            reservation.guest_count or 0,
            reservation.status,
            reservation.notes or '',
            reservation.customer.user.email if reservation.customer and reservation.customer.user else '',
            reservation.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(reservation, 'created_at') and reservation.created_at else ''
        ])
    
    return response

@admin_login_required
def export_reviews_csv(request):
    search = request.GET.get('search', '')
    reviews_list = Review.objects.all()
    
    if search:
        reviews_list = reviews_list.filter(
            Q(restaurant__name__icontains=search) |
            Q(comment__icontains=search) |
            Q(customer__user__email__icontains=search)
        )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reviews_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Restaurant', 'Customer Email', 'Rating', 'Comment', 'Created At'])
    
    for review in reviews_list.order_by('-created_at'):
        writer.writerow([
            review.restaurant.name if review.restaurant else '',
            review.customer.user.email if review.customer and review.customer.user else 'Anonymous',
            review.rating or 0,
            review.comment or '',
            review.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(review, 'created_at') and review.created_at else ''
        ])
    
    return response
