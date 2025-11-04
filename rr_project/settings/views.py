from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.validators import MinimumLengthAndNumberValidator 
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# @login_required
def settings_view(request):
    user = request.user
    context = {
        'user': user,
        'user_profile': user
    }
    return render(request, 'settings/settings.html', context)

@login_required
@require_http_methods(["POST"])
def update_profile(request):
    """Handle profile information updates via AJAX"""
    try:
        user = request.user
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
        user = request.user
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