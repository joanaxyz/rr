from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from .validators import MinimumLengthAndNumberValidator 
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User, UserRole, Customer, Admin
from email_service.views import send_verification_email, send_password_reset_code_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Save user but mark as inactive until email verification
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                
                # Generate verification token
                user.generate_verification_token()
                
                # Send verification email
                if send_verification_email(user, request):
                    messages.success(
                        request, 
                        'Registration successful! A verification email has been sent to your email address. '
                        'Please check your email and click the verification link to activate your account.'
                    )
                    return redirect('accounts:login')
                else:
                    messages.error(request, 'Account created but failed to send verification email. Please contact support.')
                    return redirect('accounts:login')
                    
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
        else:
            # Get the first error message for display
            first_error = None
            if form.non_field_errors():
                first_error = form.non_field_errors()[0]
            elif form.errors:
                # Get first field error
                first_error_list = next(iter(form.errors.values()))
                if first_error_list:
                    first_error = first_error_list[0]
    else:
        form = CustomUserCreationForm()
        first_error = None
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'first_error': first_error
    })


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.banned:
                messages.error(request, 'Your account has been banned. Please contact support.')
                return render(request, 'accounts/login.html', {'form': form})
            elif not user.email_verified:
                messages.error(request, 'Please verify your email address before logging in. Check your email for the verification link.')
                return render(request, 'accounts/login.html', {'form': form})
            else:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                # Check if there's a next parameter for redirection
                next_url = request.GET.get('next', 'home:home')
                return redirect(next_url)
        else:
            # Get the first error message
            first_error = None
            if form.non_field_errors():
                first_error = form.non_field_errors()[0]
            elif form.errors:
                # Get first field error
                first_error_list = next(iter(form.errors.values()))
                if first_error_list:
                    first_error = first_error_list[0]
    else:
        form = CustomAuthenticationForm()
        first_error = None
    
    return render(request, 'accounts/login.html', 
        {'form': form,
         'first_error': first_error,
        })

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


def forgot_password_view(request):
    """Handle forgot password process - Step 1: Email submission"""
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
    
    return render(request, 'accounts/forgot_pass.html')


def verify_reset_code_view(request):
    """Handle password reset verification - Step 2: Code verification"""
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
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def reset_password_view(request):
    """Handle password reset - Step 3: New password setup"""
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
                    
                    messages.success(request, 'Your password has been reset successfully! You can now log in with your new password.')
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
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def resend_reset_code_view(request):
    """Resend password reset code"""
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
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})





def verify_email_view(request, token):
    """Verify email address using token"""
    try:
        user = get_object_or_404(User, verification_token=token)
        
        # Check if token is expired
        if user.verification_token_expires and user.verification_token_expires < timezone.now():
            messages.error(request, 'Verification token has expired. Please sign up again.')
            user.delete()  # Remove the unverified user
            return redirect('accounts:register')
        
        # Activate user and mark email as verified
        user.is_active = True
        user.email_verified = True
        user.verification_token_expires = None
        user.save()
        
        # Create appropriate profile based on role
        if user.role == UserRole.ADMIN:
            Admin.objects.get_or_create(user=user)
        else:
            Customer.objects.get_or_create(user=user)
        
        messages.success(request, 'Email verified successfully! You can now log in to your account.')
        return redirect('accounts:login')
        
    except User.DoesNotExist:
        messages.error(request, 'Invalid or expired verification token.')
        return redirect('accounts:register')


def resend_verification_email_view(request, user_id):
    """Resend verification email"""
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
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

