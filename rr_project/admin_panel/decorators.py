from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_login_required(function):
    """
    Custom decorator that redirects unauthenticated users to the admin login page
    and checks if the user is a staff member.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_panel:login')
        
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access the admin panel.")
            return redirect('admin_panel:login')
        
        return function(request, *args, **kwargs)
    return wrap

