from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from accounts.forms import CustomUserCreationForm, CustomAuthenticationForm
from accounts.models import Owner


def restaurant_login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user.banned:
                messages.error(request, "Your account has been banned.")
                return render(request, "manage_restaurant/auth/login.html", {
                    "form": form,
                    "auth_type": "restaurant"
                })

            if not user.email_verified:
                messages.error(request, "Please verify your email before logging in.")
                return render(request, "manage_restaurant/auth/login.html", {
                    "form": form,
                    "auth_type": "restaurant"
                })

            if user.role not in ['OWNER', 'HOST', 'MANAGER']:
                messages.error(request, "You don't have permission to access restaurant management.")
                return render(request, "manage_restaurant/auth/login.html", {
                    "form": form,
                    "auth_type": "restaurant"
                })

            login(request, user)
            next_url = request.GET.get("next", "manage_restaurant:list")
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
        request, 
        "manage_restaurant/auth/login.html", 
        {
            "form": form, 
            "first_error": first_error,
            "auth_type": "restaurant"
        }
    )

def restaurant_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("manage_restaurant:login")
