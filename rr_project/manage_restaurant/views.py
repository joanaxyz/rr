from django.shortcuts import render, redirect, get_object_or_404
from restaurants.models import Restaurant, Table
from reservations.models import Reservation
from accounts.models import Owner
from django.contrib.auth.decorators import login_required

@login_required
def manage_restaurants(request):
    # show restaurants the user owns
    owner = get_object_or_404(Owner, user=request.user)
    restaurants = Restaurant.objects.filter(owner=owner)
    return render(request, "manage_restaurant/manage_list.html", {"restaurants": restaurants})

@login_required
def manage_restaurant_detail(request, restaurant_id):
    owner = get_object_or_404(Owner, user=request.user)
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=owner)
    tables = Table.objects.filter(restaurant=restaurant)
    reservations = Reservation.objects.filter(table__restaurant=restaurant)
    return render(request, "manage_restaurant/detail.html", {"restaurant": restaurant, "tables": tables, "reservations": reservations})
