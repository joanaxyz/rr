
from django.contrib.auth.decorators import login_required

from django.shortcuts import render

from .models import *
from restaurants.models import Table, Element, Floorplan
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReservationForm
from email_service.views import send_reservation_updated_email
from django.contrib import messages
import json

@login_required
def reservation(request, restaurant_id):
    """Reservation page for a specific restaurant"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    reserve_form = None
    floorplan = get_object_or_404(Floorplan, restaurant=restaurant)
    tables = Table.objects.filter(floorplan=floorplan)
    elements = Element.objects.filter(floorplan=floorplan)
    if request.method == 'POST':
        reserve_form = ReservationForm(request.POST, restaurant=restaurant)
        if reserve_form.is_valid():
            try:
                customer = get_object_or_404(Customer,user=request.user)
                reservation = reserve_form.save(commit=False)
                reservation.customer = customer
                reservation.restaurant = restaurant
                reservation.save()
                
                messages.success(request, f'Reservation created! You will receive an email once a staff has confirmed your reservation.')
                return redirect('restaurants:restaurant_detail', restaurant_id=restaurant.id)
            except Exception as e:
                messages.error(request, f'An error occured during reservation: {str(e)}')
    else:
        reserve_form = ReservationForm(initial={
            'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email
        }, restaurant=restaurant)

    context = {
        'restaurant': restaurant.to_dict(),
        'floorplan': json.dumps(floorplan.to_dict()),
        'tables': json.dumps([t.to_dict() for t in tables]),
        'elements': json.dumps([e.to_dict() for e in elements]),
        'reserve_form': reserve_form,
    }
    return render(request, 'reservations/reservation.html', context)

@login_required
def reservation_management_view(request):
    """Display, cancel, and restore reservations"""
    customer, created = Customer.objects.get_or_create(user=request.user)
    reservations = Reservation.objects.filter(customer=customer).order_by('-date')

    if request.method == 'POST':
        # Cancel reservation
        if 'cancel_reservation' in request.POST:
            reservation_id = request.POST.get('cancel_reservation')
            reason = request.POST.get('cancel_reason', '').strip()

            try:
                reservation = get_object_or_404(Reservation, id=reservation_id, customer=customer)
                restaurant_name = reservation.restaurant.name if reservation.restaurant else "Unknown Restaurant"
                reservation.status = 'CANCELLED'
                reservation.cancellation_info = {
                    "reason": reason,
                    "sender": request.user.username,
                }
                reservation.save()
                messages.success(request, f"Reservation at {restaurant_name} has been cancelled.")
            except Exception:
                messages.error(request, "Failed to cancel reservation. Please try again.")
            return redirect('reservations:reservation_management')

        # Restore reservation
        elif 'restore_reservation' in request.POST:
            reservation_id = request.POST.get('restore_reservation')
            try:
                reservation = get_object_or_404(Reservation, id=reservation_id, customer=customer)
                if reservation.status == 'CANCELLED':
                    reservation.status = 'PENDING'
                    reservation.cancellation_info = {}
                    reservation.save()
                    messages.success(request, f"Reservation has been restored.")
                else:
                    messages.warning(request, "Only cancelled reservations can be restored.")
            except Exception:
                messages.error(request, "Failed to restore reservation. Please try again.")
            return redirect('reservations:reservation_management')

    context = {
        'reservations': reservations,
        'has_reservations': reservations.exists(),
    }
    return render(request, 'reservations/reservation_list.html', context)

@login_required
def edit_reservation(request, reservation_id):
    """Edit an existing reservation"""
    customer = get_object_or_404(Customer, user=request.user)
    reservation = get_object_or_404(Reservation, id=reservation_id, customer=customer)

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation, restaurant=reservation.restaurant)
        if form.is_valid():
            updated_reservation = form.save()
            
            # Send update notification email
            send_reservation_updated_email(updated_reservation)
            
            messages.success(request, 'Your reservation has been updated successfully. A confirmation email has been sent.')
            return redirect('reservations:reservation_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReservationForm(instance=reservation, restaurant=reservation.restaurant)
    
    floorplan = get_object_or_404(Floorplan, restaurant=reservation.restaurant)
    tables = Table.objects.filter(floorplan=floorplan)
    elements = Element.objects.filter(floorplan=floorplan)
    context = {
        'restaurant': reservation.restaurant.to_dict(),
        'tables': json.dumps([t.to_dict() for t in tables]),
        'elements': json.dumps([e.to_dict() for e in elements]),
        'floorplan': json.dumps(floorplan.to_dict()),
        'reserve_form': form,
        'edit_mode': True,
    }
    return render(request, 'reservations/reservation.html', context)
