from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.validators import MinimumLengthAndNumberValidator 
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@login_required
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
        
        # Validate email
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        # Validate email uniqueness (exclude current user)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            return JsonResponse({'success': False, 'message': 'This email is already in use by another account'})
        
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
        
        # Validate all fields are provided
        if not all([current_password, new_password, confirm_password]):
            return JsonResponse({'success': False, 'message': 'All fields are required'})
        
        # Verify current password
        if not check_password(current_password, user.password):
            return JsonResponse({'success': False, 'message': 'Current password is incorrect'})
        
        # Check passwords match
        if new_password != confirm_password:
            return JsonResponse({'success': False, 'message': 'New passwords do not match'})
        
        # Validate new password
        validator = MinimumLengthAndNumberValidator(min_length=8)
        try:
            validator.validate(new_password)
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': e.messages[0] if e.messages else 'Password validation failed'})
        
        # Check new password is different from current
        if check_password(new_password, user.password):
            return JsonResponse({'success': False, 'message': 'New password cannot be the same as current password'})
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({'success': True, 'message': 'Password updated successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})