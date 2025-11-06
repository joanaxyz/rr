from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password

from .models import User
from .validators import MinimumLengthAndNumberValidator
from email_service.views import send_verification_email, send_password_reset_code_email


def api_forgot_password(request):
    """API endpoint for password reset - Step 1: Email submission"""
    if request.method == 'POST':
        try:
            data = request.POST
            email = data.get('email', '').strip()
            
            if not email:
                return JsonResponse({
                    'success': False, 
                    'message': 'Email address is required.'
                })
            
            # Find user by email
            try:
                user = User.objects.get(email=email, is_active=True)
                
                # Generate password reset code
                reset_code = user.generate_password_reset_code()
                
                # Send email with code
                if send_password_reset_code_email(user, reset_code):
                    return JsonResponse({
                        'success': True,
                        'message': 'Verification code sent to your email address.',
                        'user_id': user.id
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Failed to send verification code. Please try again.'
                    })
                    
            except User.DoesNotExist:
                # For security, don't reveal if email exists
                return JsonResponse({
                    'success': True,
                    'message': 'If an account with this email exists, you will receive a verification code.',
                    'user_id': None
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            })
    
    return JsonResponse({'success': False, 'message': 'Only POST allowed'}, status=400)


def api_verify_reset_code(request):
    """API endpoint for password reset - Step 2: Code verification"""
    if request.method == 'POST':
        try:
            data = request.POST
            user_id = data.get('user_id')
            code = data.get('code', '').strip()
            
            if not user_id or not code:
                return JsonResponse({
                    'success': False,
                    'message': 'User ID and verification code are required.'
                })
            
            try:
                user = User.objects.get(id=user_id, is_active=True)
                
                if user.is_password_reset_code_valid(code):
                    return JsonResponse({
                        'success': True,
                        'message': 'Code verified successfully.',
                        'user_id': user_id,
                        'verified_code': code
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid or expired verification code.'
                    })
                    
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid user.'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            })
    
    return JsonResponse({'success': False, 'message': 'Only POST allowed'}, status=400)


def api_reset_password(request):
    """API endpoint for password reset - Step 3: New password setup"""
    if request.method == 'POST':
        try:
            data = request.POST
            user_id = data.get('user_id')
            code = data.get('code')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
            
            if not all([user_id, code, new_password, confirm_password]):
                return JsonResponse({
                    'success': False,
                    'message': 'All fields are required.'
                })
            
            if new_password != confirm_password:
                return JsonResponse({
                    'success': False,
                    'message': 'Passwords do not match.'
                })
            
            validator = MinimumLengthAndNumberValidator(min_length=8)
            try:
                validator.validate(new_password)
            except ValidationError as e:
                return JsonResponse({
                    'success': False,
                    'message': e.messages[0]
                })
        
            try:
                user = User.objects.get(id=user_id, is_active=True)
                
                if check_password(new_password, user.password):
                    return JsonResponse({
                        'success': False,
                        'message': 'The new password cannot be the same as the old password.'
                    })
                
                # Verify code one more time
                if user.is_password_reset_code_valid(code):
                    # Set new password
                    user.set_password(new_password)
                    user.clear_password_reset_code()
                    user.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Password reset successfully.',
                        'redirect_url': reverse('accounts:login')
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid or expired verification code.'
                    })
                    
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid user.'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            })
    
    return JsonResponse({'success': False, 'message': 'Only POST allowed'}, status=400)


def api_resend_reset_code(request):
    """API endpoint for resending password reset code"""
    if request.method == 'POST':
        try:
            data = request.POST
            user_id = data.get('user_id')
            
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'message': 'User ID is required.'
                })
            
            try:
                user = User.objects.get(id=user_id, is_active=True)
                
                # Generate new reset code
                reset_code = user.generate_password_reset_code()
                
                # Send email
                if send_password_reset_code_email(user, reset_code):
                    return JsonResponse({
                        'success': True,
                        'message': 'New verification code sent to your email address.'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Failed to send verification code. Please try again.'
                    })
                    
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid user.'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            })
    
    return JsonResponse({'success': False, 'message': 'Only POST allowed'}, status=400)


def api_resend_verification_email(request, user_id):
    """API endpoint for resending verification email"""
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=user_id, is_active=False, email_verified=False)
            
            # Generate new token
            user.generate_verification_token()
            
            # Send email
            if send_verification_email(user, request):
                return JsonResponse({
                    'success': True, 
                    'message': 'Verification email sent successfully!'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'message': 'Failed to send verification email. Please try again.'
                })
                
        except User.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid user or user already verified.'
            })
    
    return JsonResponse({'success': False, 'message': 'Only POST allowed'}, status=400)