from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def owner_verification(request):
    return render(request, 'owner_verification/register_restaurant.html')
