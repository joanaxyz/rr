
from django.contrib.auth.decorators import login_required

from django.shortcuts import render

from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReservationForm

from django.contrib import messages


@login_required
def reservation(request, restaurant_id):
    """Reservation page for a specific restaurant"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    reserve_form = None

    if request.method == 'POST':
        reserve_form = ReservationForm(request.POST, restaurant=restaurant)
        if reserve_form.is_valid():
            try:
                customer = Customer.objects.filter(user=request.user).first()
                reservation = reserve_form.save(commit=False)
                reservation.customer = customer
                reservation.restaurant = restaurant
                reservation.save()

                messages.success(request, f'You will receive an email once your reservation has been confirmed')
                return redirect('restaurants:restaurant_detail', restaurant_id=restaurant.id)
            except Exception as e:
                messages.error(request, f'An error occured during reservation: {str(e)}')
    else:
        reserve_form = ReservationForm(initial={
            'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email
        }, restaurant=restaurant)

    context = {
        'restaurant': restaurant,
        'reserve_form': reserve_form,
    }
    return render(request, 'reservations/reservation.html', context)

@login_required
def reservation_management_view(request):
    """Display, cancel, delete, or edit reservations"""
    customer, created = Customer.objects.get_or_create(user=request.user)
    reservations = Reservation.objects.filter(customer=customer).order_by('-date')

    if request.method == 'POST':
        # Cancel reservation
        if 'cancel_reservation' in request.POST:
            reservation_id = request.POST.get('cancel_reservation')
            reason = request.POST.get('cancellation_reason', '').strip()

            try:
                reservation = get_object_or_404(Reservation, id=reservation_id, customer=customer)
                restaurant_name = reservation.restaurant.name if reservation.restaurant else "Unknown Restaurant"
                reservation.status = 'CANCELLED'
                reservation.cancellation_reason = reason
                reservation.save()
                messages.success(request, f"Reservation at {restaurant_name} has been cancelled.")
            except Exception:
                messages.error(request, "Failed to cancel reservation. Please try again.")
            return redirect('reservations:reservation_management')

        # Delete reservation
        elif 'delete_reservation' in request.POST:
            reservation_id = request.POST.get('delete_reservation')
            try:
                reservation = get_object_or_404(Reservation, id=reservation_id, customer=customer)
                reservation.delete()
                messages.success(request, "Cancelled reservation has been deleted.")
            except Exception:
                messages.error(request, "Failed to delete reservation. Please try again.")
            return redirect('reservations:reservation_management')

        # Edit reservation
        elif 'edit_reservation' in request.POST:
            reservation_id = request.POST.get('reservation_id')
            new_date = request.POST.get('edit_date')
            new_time = request.POST.get('edit_time')
            new_guest_count = request.POST.get('edit_guest_count')
            new_notes = request.POST.get('edit_notes', '')

            try:
                reservation = get_object_or_404(Reservation, id=reservation_id, customer=customer)
                reservation.date = new_date
                reservation.time = new_time
                reservation.guest_count = new_guest_count
                reservation.notes = new_notes
                reservation.save()
                messages.success(request, f"Reservation at {reservation.restaurant.name} has been updated.")
            except Exception as e:
                messages.error(request, f"Failed to update reservation: {str(e)}")
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
            form.save()
            messages.success(request, 'Your reservation has been updated successfully.')
            return redirect('reservations:reservation_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReservationForm(instance=reservation, restaurant=reservation.restaurant)

    context = {
        'restaurant': reservation.restaurant,
        'reserve_form': form,
        'edit_mode': True,
    }
    return render(request, 'reservations/reservation.html', context)
