from django.shortcuts import render
from .forms import OwnerForm


# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from .validators import MinimumLengthAndNumberValidator 
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import *
from email_service.views import send_verification_email, send_password_reset_code_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['role'] = 'CUSTOMER'
        form = CustomUserCreationForm(post_data)
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
        form = CustomUserCreationForm(initial={
            'role': 'CUSTOMER'
        })
        first_error = None
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'first_error': first_error
    })

def register_staff_view(request, email, role, restaurant_id):
    """User registration view"""
    first_error = None
    
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['username'] = email
        post_data['role'] = role
        form = CustomUserCreationForm(post_data)
        if form.is_valid():
            try:
                # Save user but mark as inactive until email verification
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                
                # Generate verification token
                user.generate_verification_token()
                
                from email_service.views import send_staff_verification_email
                # Send verification email
                if send_staff_verification_email(user, request, restaurant_id):
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
            if form.non_field_errors():
                first_error = form.non_field_errors()[0]
            elif form.errors:
                # Get first field error
                first_error_list = next(iter(form.errors.values()))
                if first_error_list:
                    first_error = first_error_list[0]
    else:
        form = CustomUserCreationForm(initial={
            'username': email,
            'role': role,
        })
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'first_error': first_error,
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



def invite_staff(request, user_id, role, restaurant_id):
    user = get_object_or_404(User, id=user_id)
    user.role = role

    from restaurants.models import Restaurant
    restaurant = get_object_or_404(Restaurant, id = restaurant_id)

    if role == 'MANAGER':
        from accounts.models import Manager
        manager = Manager.objects.create(user=user)
        restaurant.managers.add(manager)
    else:
        from accounts.models import Host
        host = Host.objects.create(user=user)
        restaurant.hosts.add(host)
    
    restaurant.save()

    messages.success(request, '')
    return redirect('accounts:login')
    


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
        
        messages.success(request, 'Email verified successfully! You can now log in to your account.')
        return redirect('accounts:login')
        
    except User.DoesNotExist:
        messages.error(request, 'Invalid or expired verification token.')
        return redirect('accounts:register')

def verify_staff_email_view(request, token, restaurant_id):
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

        from restaurants.models import Restaurant

        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        if user.role == 'MANAGER':
            from accounts.models import Manager
            manager = Manager.objects.create(user=user)
            restaurant.managers.add(manager)
        elif user.role == 'HOST':
            from accounts.models import Host
            host = Host.objects.create(user=user)
            restaurant.hosts.add(host)
        restaurant.save()
        
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

def apply_owner(request):
    if request.method == 'POST':
        form = OwnerForm(request.POST, request.FILES)
        if form.is_valid():
            owner = form.save(commit=False)
            owner.user = request.user
            owner.save()
            return redirect('accounts:apply_owner')
        else:
            print("Form is invalid:", form.errors)
    else:
        form = OwnerForm()

    return render(request, 'accounts/apply_owner.html', {'form': form})
