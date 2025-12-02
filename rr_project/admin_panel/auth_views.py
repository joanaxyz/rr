from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from accounts.forms import CustomAuthenticationForm


def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_panel:dashboard')
        else:
            messages.error(request, "You don't have permission to access the admin panel.")
            logout(request)
    
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user.banned:
                messages.error(request, "Your account has been banned.")
                return render(request, "admin_panel/auth/login.html", {
                    "form": form,
                })

            if not user.is_staff:
                messages.error(request, "You don't have permission to access the admin panel.")
                return render(request, "admin_panel/auth/login.html", {
                    "form": form,
                })

            login(request, user)
            next_url = request.GET.get("next", "admin_panel:dashboard")
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
        "admin_panel/auth/login.html", 
        {
            "form": form, 
            "first_error": first_error,
        }
    )


def admin_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("admin_panel:login")

