from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import json

from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
)
from .models import *
from restaurants.models import Bookmark, Review
from email_service.views import send_verification_email, send_password_reset_code_email
from owner_verification.supabase_utils import upload_to_supabase
import uuid


# ------------------------------
# USER REGISTRATION
# ------------------------------
def register_view(request):
    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["role"] = "CUSTOMER"
        form = CustomUserCreationForm(post_data)

        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                user.generate_verification_token()

                if send_verification_email(user, request):
                    messages.success(
                        request,
                        "Registration successful! A verification email has been sent.",
                    )
                    return redirect("accounts:login")
                else:
                    messages.error(
                        request,
                        "Account created but failed to send verification email.",
                    )
                    return redirect("accounts:login")

            except Exception as e:
                messages.error(request, f"Error during registration: {str(e)}")

        else:
            first_error = None
            if form.non_field_errors():
                first_error = form.non_field_errors()[0]
            elif form.errors:
                first_error_list = next(iter(form.errors.values()))
                if first_error_list:
                    first_error = first_error_list[0]

    else:
        form = CustomUserCreationForm(initial={"role": "CUSTOMER"})
        first_error = None

    return render(
        request,
        "accounts/register.html",
        {"form": form, "first_error": first_error},
    )


# ------------------------------
# STAFF REGISTRATION
# ------------------------------
def register_staff_view(request, email, role, restaurant_id):
    first_error = None

    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["username"] = email
        post_data["role"] = role

        form = CustomUserCreationForm(post_data)

        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                user.generate_verification_token()

                from email_service.views import send_staff_verification_email

                if send_staff_verification_email(user, request, restaurant_id):
                    messages.success(
                        request,
                        "Staff account created! Verification email has been sent.",
                    )
                    return redirect("accounts:login")
                else:
                    messages.error(
                        request, "Account created but failed to send verification email."
                    )

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")

        else:
            if form.non_field_errors():
                first_error = form.non_field_errors()[0]
            elif form.errors:
                first_error_list = next(iter(form.errors.values()))
                if first_error_list:
                    first_error = first_error_list[0]

    else:
        form = CustomUserCreationForm(initial={"username": email, "role": role})

    return render(
        request,
        "accounts/register.html",
        {"form": form, "first_error": first_error},
    )


# ------------------------------
# LOGIN
# ------------------------------
def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user.banned:
                messages.error(request, "Your account has been banned.")
                return render(request, "accounts/login.html", {"form": form})

            if not user.email_verified:
                messages.error(request, "Please verify your email before logging in.")
                return render(request, "accounts/login.html", {"form": form})

            login(request, user)

            next_url = request.GET.get("next", "home:home")
            return redirect(next_url)

        else:
            first_error = None
            if form.non_field_errors():
                first_error = form.non_field_errors()[0]
            elif form.errors:
                first_error_list = next(iter(form.errors.values()))
                if first_error_list:
                    first_error = first_error_list[0]

    else:
        form = CustomAuthenticationForm()
        first_error = None

    return render(
        request, "accounts/login.html", {"form": form, "first_error": first_error}
    )


# ------------------------------
# LOGOUT
# ------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:login")


# ------------------------------
# FORGOT PASSWORD
# ------------------------------
def forgot_password_view(request):
    return render(request, "accounts/forgot_pass.html")


# ------------------------------
# STAFF INVITE
# ------------------------------
def invite_staff(request, user_id, role, restaurant_id):
    user = get_object_or_404(User, id=user_id)
    user.role = role

    from restaurants.models import Restaurant

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if role == "MANAGER":
        from accounts.models import Manager

        manager = Manager.objects.create(user=user)
        restaurant.managers.add(manager)
    else:
        from accounts.models import Host

        host = Host.objects.create(user=user)
        restaurant.hosts.add(host)

    restaurant.save()

    messages.success(request, "Staff invited successfully.")
    return redirect("accounts:login")


# ------------------------------
# EMAIL VERIFICATION
# ------------------------------
def verify_email_view(request, token):
    try:
        user = get_object_or_404(User, verification_token=token)

        if (
            user.verification_token_expires
            and user.verification_token_expires < timezone.now()
        ):
            messages.error(request, "Verification token expired.")
            user.delete()
            return redirect("accounts:register")

        user.is_active = True
        user.email_verified = True
        user.verification_token_expires = None
        user.save()

        messages.success(request, "Email verified!")
        return redirect("accounts:login")

    except User.DoesNotExist:
        messages.error(request, "Invalid verification token.")
        return redirect("accounts:register")


def verify_staff_email_view(request, token, restaurant_id):
    try:
        user = get_object_or_404(User, verification_token=token)

        if (
            user.verification_token_expires
            and user.verification_token_expires < timezone.now()
        ):
            messages.error(request, "Verification token expired.")
            user.delete()
            return redirect("accounts:register")

        user.is_active = True
        user.email_verified = True
        user.verification_token_expires = None
        user.save()

        from restaurants.models import Restaurant

        restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        if user.role == "MANAGER":
            from accounts.models import Manager

            manager = Manager.objects.create(user=user)
            restaurant.managers.add(manager)
        elif user.role == "HOST":
            from accounts.models import Host

            host = Host.objects.create(user=user)
            restaurant.hosts.add(host)

        restaurant.save()

        messages.success(request, "Staff email verified!")
        return redirect("accounts:login")

    except User.DoesNotExist:
        messages.error(request, "Invalid token.")
        return redirect("accounts:register")


# ------------------------------
# RESEND VERIFICATION EMAIL
# ------------------------------
def resend_verification_email_view(request, user_id):
    if request.method == "POST":
        try:
            user = get_object_or_404(
                User, id=user_id, is_active=False, email_verified=False
            )

            user.generate_verification_token()

            if send_verification_email(user, request):
                return JsonResponse(
                    {"success": True, "message": "Verification email sent!"}
                )
            else:
                return JsonResponse(
                    {"success": False, "message": "Failed to send email."}
                )

        except User.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Invalid or already verified user."}
            )

    return JsonResponse({"success": False, "message": "Invalid request method."})


# ------------------------------
# USER PROFILE
# ------------------------------
@login_required
def profile_view(request):
    """Display user profile with bookmarked restaurants and reviews"""
    customer, _ = Customer.objects.get_or_create(user=request.user)
    
    # Handle profile image upload
    if request.method == 'POST' and 'update_profile_image' in request.POST:
        profile_image_file = request.FILES.get('profile_image')
        
        if profile_image_file:
            try:
                # Upload to Supabase
                file_path = f"profile_images/{uuid.uuid4()}_{profile_image_file.name}"
                image_url = upload_to_supabase(profile_image_file, "files", file_path)
                
                if image_url:
                    request.user.profile_image = image_url
                    request.user.save()
                    messages.success(request, 'Profile image updated successfully!')
                else:
                    messages.error(request, 'Failed to upload profile image. Please try again.')
            except Exception as e:
                messages.error(request, f'Error uploading image: {str(e)}')
        else:
            messages.error(request, 'Please select an image file.')
        
        return redirect('accounts:profile')
    
    # Get bookmarked restaurants
    bookmarks = Bookmark.objects.filter(customer=customer).select_related('restaurant').order_by('-created_at')
    bookmarked_restaurants = [bookmark.restaurant for bookmark in bookmarks]
    
    # Get user reviews
    reviews = Review.objects.filter(customer=customer).select_related('restaurant').order_by('-created_at')
    
    # Annotate restaurants with ratings
    from django.db.models import Avg, Count
    for restaurant in bookmarked_restaurants:
        restaurant_reviews = Review.objects.filter(restaurant=restaurant)
        restaurant.avg_rating = restaurant_reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        restaurant.review_count = restaurant_reviews.count()
    
    context = {
        'user': request.user,
        'customer': customer,
        'bookmarked_restaurants': bookmarked_restaurants,
        'reviews': reviews,
        'bookmark_count': bookmarks.count(),
        'review_count': reviews.count(),
    }
    
    return render(request, 'accounts/profile.html', context)