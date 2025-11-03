from django.shortcuts import render, redirect, get_object_or_404
from .models import Restaurant, Table, Reservation
from django.contrib.auth.decorators import login_required

@login_required
def manage_restaurants(request):
    # show restaurants the user owns
    restaurants = Restaurant.objects.filter(owner=request.user)
    return render(request, "manage_restaurant/manage_list.html", {"restaurants": restaurants})

@login_required
def manage_restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk, owner=request.user)
    tables = restaurant.table_set.all()
    reservations = Reservation.objects.filter(table__restaurant=restaurant)
    return render(request, "manage_restaurant/detail.html", {"restaurant": restaurant, "tables": tables, "reservations": reservations})
