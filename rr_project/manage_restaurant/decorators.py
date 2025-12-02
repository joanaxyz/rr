from django.contrib.auth.decorators import login_required as django_login_required
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def restaurant_login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('manage_restaurant:login')
        
        if request.user.role not in ['OWNER', 'HOST', 'MANAGER']:
            messages.error(request, "You don't have permission to access restaurant management.")
            return redirect('manage_restaurant:login')
        
        return function(request, *args, **kwargs)
    return wrap
