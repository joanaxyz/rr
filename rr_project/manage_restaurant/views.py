from django.shortcuts import render, redirect, get_object_or_404
from restaurants.models import Restaurant, Table, Element, Floorplan
from reservations.models import Reservation, TableReservation
from accounts.models import Owner
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from email_service.views import send_reservation_cancellation_email, send_reservation_confirmation_email, send_reservation_completion_email
import json
@login_required
def view_restaurants(request):
    # show restaurants the user owns
    owner = get_object_or_404(Owner, user=request.user)
    restaurants = Restaurant.objects.filter(owner=owner)
    restaurants_dicts = [r.to_dict() for r in restaurants]
    return render(request, "manage_restaurant/list.html", {"restaurants": restaurants_dicts})
@login_required
def manage_reservations(request, restaurant_id):
    owner = get_object_or_404(Owner, user=request.user)
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=owner)
    reservations = Reservation.objects.filter(restaurant=restaurant)
    floorplan = get_object_or_404(Floorplan, restaurant=restaurant)
    tables = Table.objects.filter(floorplan=floorplan)
    elements = Element.objects.filter(floorplan=floorplan)
    if request.method == 'POST':
        data = request.POST
        reservation_id = data.get('reservation_id')
        reservation = get_object_or_404(Reservation, id=reservation_id)
        if data.get('action') == 'confirm':
            reservation.status = 'CONFIRMED'
            reservation.save()
            for number in reservation.table_numbers:
                table = Table.objects.get(floorplan=restaurant.floorplan, number=number)
                table.status = 'RESERVED'
                table.save()
                table_reservation = TableReservation.objects.create(
                    table=table,
                    reservation=reservation
                )
                table_reservation.save()
            if send_reservation_confirmation_email(reservation):
                messages.success(request, f"Confirmation email to {reservation.customer.user.first_name} has been sent")
        elif data.get('action') == 'complete':
            reservation.status = 'COMPLETED'
            for number in reservation.table_numbers:
                table = Table.objects.get(floorplan=restaurant.floorplan, number=number)
                table.status = 'AVAILABLE'
                table.save()
                table_reservation = TableReservation.objects.filter(
                    table=table,
                    reservation=reservation
                )
                table_reservation.delete()
            reservation.save()
            if send_reservation_completion_email(reservation):
                messages.success(request, f"Thank you email to {reservation.customer.user.first_name} has been sent")
        elif data.get('action') == 'delete':
            reservation.delete()
        else:
            reason = data.get('cancellation_reason')
            reservation.cancellation_info = {
                'reason': reason,
                'sender': 'HOST'
            }
            for number in reservation.table_numbers:
                table = Table.objects.get(floorplan=restaurant.floorplan, number=number)
                table.status = 'AVAILABLE'
                table.save()
                table_reservation = TableReservation.objects.filter(
                    table=table,
                    reservation=reservation
                )
                table_reservation.delete()
            reservation.delete()
            if send_reservation_cancellation_email(reservation):
                messages.success(request, f"Cancellation email to {reservation.customer.user.first_name} has been sent")
        return redirect('manage_restaurant:reservations', restaurant_id=restaurant_id)
    
    context = {
        "restaurant": restaurant.to_dict(),
        "reservations": [r.to_dict() for r in reservations],
        "has_reservations": reservations.exists(),
        'floorplan': json.dumps(floorplan.to_dict()),
        "tables": json.dumps([t.to_dict() for t in tables]),
        "elements": json.dumps([e.to_dict() for e in elements])
    }
    return render(request, "manage_restaurant/manage_reservation.html", context)

@login_required
def manage_tables(request, restaurant_id):
    owner = get_object_or_404(Owner, user=request.user)
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=owner)
    floorplan = get_object_or_404(Floorplan, restaurant=restaurant)
    tables = Table.objects.filter(floorplan=floorplan)
    elements = Element.objects.filter(floorplan=floorplan)
    context = {
        "restaurant_id": restaurant_id,
        'floorplan': json.dumps(floorplan.to_dict()),
        "tables": json.dumps([t.to_dict() for t in tables]),
        "elements": json.dumps([e.to_dict() for e in elements])
    }
    return render(request, "manage_restaurant/manage_tables.html", context)

@login_required
def manage_details(request, restaurant_id):
    owner = get_object_or_404(Owner, user=request.user)
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=owner)
    
    if request.method == 'POST':
        try:
            # Update basic information
            restaurant.name = request.POST.get('name', restaurant.name)
            restaurant.phone_number = request.POST.get('phone_number', restaurant.phone_number)
            restaurant.email = request.POST.get('email', restaurant.email)
            restaurant.description = request.POST.get('description', restaurant.description)
            
            # Update address information
            restaurant.street_number = request.POST.get('street_number', restaurant.street_number)
            restaurant.street_name = request.POST.get('street_name', restaurant.street_name)
            restaurant.street_block = request.POST.get('street_block', restaurant.street_block)
            restaurant.city = request.POST.get('city', restaurant.city)
            restaurant.postal_code = request.POST.get('postal_code', restaurant.postal_code)
            
            # Update operating hours
            opening_time = request.POST.get('opening_time')
            if opening_time:
                restaurant.opening_time = opening_time
            
            closing_time = request.POST.get('closing_time')
            if closing_time:
                restaurant.closing_time = closing_time
            
            restaurant.operating_days = request.POST.get('operating_days', restaurant.operating_days)
            
            # Update pricing and capacity
            price_min = request.POST.get('price_min')
            if price_min:
                restaurant.price_min = float(price_min)
            
            price_max = request.POST.get('price_max')
            if price_max:
                restaurant.price_max = float(price_max)
            
            restaurant.max_guest_count = request.POST.get('max_guest_count', restaurant.max_guest_count)
            
            # Handle image upload
            if 'image' in request.FILES:
                restaurant.image = request.FILES['image']
            
            restaurant.save()
            messages.success(request, 'Restaurant details updated successfully!')
            return redirect('manage_restaurant:details', restaurant_id=restaurant_id)
        
        except Exception as e:
            messages.error(request, f'Error updating restaurant details: {str(e)}')
    
    context = {
        "restaurant": restaurant.to_dict(),
    }
    return render(request, "manage_restaurant/manage_details.html", context)

@login_required
def dashboard(request, restaurant_id):
    owner = get_object_or_404(Owner, user=request.user)
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=owner)
    
    # Get statistics
    total_reservations = Reservation.objects.filter(restaurant=restaurant).count()
    pending_reservations = Reservation.objects.filter(restaurant=restaurant, status='PENDING').count()
    confirmed_reservations = Reservation.objects.filter(restaurant=restaurant, status='CONFIRMED').count()
    total_tables = Table.objects.filter(floorplan=restaurant.floorplan).count()
    
    context = {
        "restaurant": restaurant.to_dict(),
        "total_reservations": total_reservations,
        "pending_reservations": pending_reservations,
        "confirmed_reservations": confirmed_reservations,
        "total_tables": total_tables,
    }
    return render(request, "manage_restaurant/dashboard.html", context)