from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.validators import MinimumLengthAndNumberValidator 
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from owner_verification.models import OwnerVerificationRequest

@login_required
def settings_view(request):
    user = request.user
    user_dict = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': user.phone_number,
        'role': user.role
    }
    
    verification_request = None
    try:
        verification_request = OwnerVerificationRequest.objects.filter(user=user).latest('created_at')
    except OwnerVerificationRequest.DoesNotExist:
        pass
    
    from restaurants.models import Restaurant
    
    staff_assignments = []
    if user.role in ['HOST', 'MANAGER']:
        if user.role == 'HOST':
            restaurants = Restaurant.objects.filter(hosts=user.host_profile)
        else:
            restaurants = Restaurant.objects.filter(managers=user.manager_profile)
        
        for restaurant in restaurants:
            staff_assignments.append({
                'restaurant_name': restaurant.name,
                'restaurant_id': restaurant.id,
                'owner_name': restaurant.owner.user.get_full_name() if restaurant.owner else 'N/A',
                'owner_email': restaurant.owner.user.email if restaurant.owner else 'N/A',
                'phone': restaurant.phone_number,
                'address': restaurant.full_address
            })
    
    owned_restaurants = []
    if user.role == 'OWNER':
        try:
            owner_profile = user.owner_profile
            restaurants = Restaurant.objects.filter(owner=owner_profile).order_by('-created_at')
            
            for restaurant in restaurants:
                owned_restaurants.append({
                    'restaurant_name': restaurant.name,
                    'restaurant_id': restaurant.id,
                    'address': restaurant.full_address,
                    'phone': restaurant.phone_number,
                    'email': restaurant.email,
                    'registered_date': restaurant.created_at.strftime('%B %d, %Y'),
                    'max_guests': restaurant.max_guest_count,
                    'price_range': restaurant.price_range_display
                })
        except:
            pass
    
    context = {
        'user_data': user_dict,
        'verification_request': verification_request,
        'staff_assignments': staff_assignments,
        'owned_restaurants': owned_restaurants
    }
    return render(request, 'settings/settings.html', context)

@login_required
@require_http_methods(["POST"])
def update_profile(request):
    """Handle profile information updates via AJAX"""
    try:
        import json
        user = request.user
        
        # Handle JSON request body
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
        else:
            # Fallback to POST data for form submissions
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
        
        errors = {}
        
        # Validate required fields
        if not first_name:
            errors['first_name'] = 'First name is required'
        
        if not last_name:
            errors['last_name'] = 'Last name is required'
        
        if not email:
            errors['email'] = 'Email is required'
        else:
            # Basic email format validation
            import re
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                errors['email'] = 'Please enter a valid email address'
            else:
                # Validate email uniqueness (exclude current user)
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    errors['email'] = 'This email is already in use by another account'
        
        # Validate phone if provided
        if phone:
            digits_only = re.sub(r'\D', '', phone)
            if len(digits_only) != 10:
                errors['phone'] = 'Phone number must be 10 digits'
        
        # Return errors if any validation failed
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone
        user.save()
        
        return JsonResponse({'success': True, 'message': 'Profile updated successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_http_methods(["POST"])
def change_password(request):
    """Handle password changes via AJAX"""
    try:
        import json
        user = request.user
        
        # Handle JSON request body
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            current_password = data.get('current_password', '').strip()
            new_password = data.get('new_password', '').strip()
            confirm_password = data.get('confirm_password', '').strip()
        else:
            # Fallback to POST data for form submissions
            current_password = request.POST.get('current_password', '').strip()
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()
        
        errors = {}
        
        # Validate required fields
        if not current_password:
            errors['current_password'] = 'Current password is required'
        
        if not new_password:
            errors['new_password'] = 'New password is required'
        
        if not confirm_password:
            errors['confirm_password'] = 'Confirm password is required'
        
        # Verify current password (only if provided)
        if current_password and not check_password(current_password, user.password):
            errors['current_password'] = 'Current password is incorrect'
        
        # Check passwords match (only if both provided)
        if new_password and confirm_password and new_password != confirm_password:
            errors['new_password'] = 'Passwords do not match'
            errors['confirm_password'] = 'Passwords do not match'
        
        # Validate new password (only if provided and not already errored)
        if new_password and 'new_password' not in errors:
            validator = MinimumLengthAndNumberValidator(min_length=8)
            try:
                validator.validate(new_password)
            except ValidationError as e:
                errors['new_password'] = e.messages[0] if e.messages else 'Password validation failed'
            
            # Check new password is different from current
            if check_password(new_password, user.password):
                errors['new_password'] = 'New password cannot be the same as current password'
        
        # Return errors if any validation failed
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({'success': True, 'message': 'Password updated successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})