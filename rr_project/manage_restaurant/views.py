from django.shortcuts import render, redirect, get_object_or_404
from restaurants.models import Restaurant, Table, Element, Floorplan, Cuisine, Tags
from reservations.models import Reservation, TableReservation
from accounts.models import Owner, User, Host, Manager
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from email_service.views import send_reservation_cancellation_email, send_reservation_confirmation_email, send_reservation_completion_email
from owner_verification.supabase_utils import upload_to_supabase
from .decorators import restaurant_login_required
import json
import csv
from datetime import datetime
import uuid

@restaurant_login_required
def view_restaurants(request):
    # show restaurants the user owns
    user = request.user
    restaurants = None
    if user.role == 'OWNER':
        owner = get_object_or_404(Owner, user=request.user)
        restaurants = owner.restaurants.all()
    elif user.role == 'HOST':
        host = get_object_or_404(Host, user=request.user)
        restaurants = Restaurant.objects.filter(hosts=host)
    elif user.role == 'MANAGER':
        manager = get_object_or_404(Manager, user=request.user)
        restaurants = Restaurant.objects.filter(managers=manager)
    restaurants_dicts = [r.to_dict() for r in restaurants]
    return render(request, "manage_restaurant/list.html", {"restaurants": restaurants_dicts})


@restaurant_login_required
def create_restaurant(request):
    """Create a restaurant creation request - only for owners"""
    if request.user.role != 'OWNER':
        messages.error(request, 'Only restaurant owners can create restaurants.')
        return redirect('manage_restaurant:list')
    
    if request.method == 'POST':
        try:
            from restaurants.models import RestaurantCreationRequest
            
            # Get form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            description = request.POST.get('description')
            
            # Address components
            street_number = request.POST.get('street_number', '')
            street_name = request.POST.get('street_name', '')
            street_block = request.POST.get('street_block', '')
            city = request.POST.get('city', '')
            postal_code = request.POST.get('postal_code', '')
            
            # Pricing
            price_min = request.POST.get('price_min', 0)
            price_max = request.POST.get('price_max', 0)
            
            # Operating details
            max_guest_count = request.POST.get('max_guest_count', 0)
            opening_time = request.POST.get('opening_time')
            closing_time = request.POST.get('closing_time')
            
            # Operating days - get from checkboxes
            operating_days_list = request.POST.getlist('operating_days')
            operating_days = ','.join(operating_days_list) if operating_days_list else 'Mon,Tue,Wed,Thu,Fri,Sat,Sun'
            
            # Custom tags
            custom_tags = request.POST.get('custom_tags', '').strip()
            
            # Validate required fields
            if not all([name, email, phone_number, description, max_guest_count]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'manage_restaurant/create_restaurant.html', {
                    'cuisines': Cuisine.objects.all(),
                    'tags': Tags.objects.all()
                })
            
            # Create restaurant creation request
            restaurant_request = RestaurantCreationRequest.objects.create(
                user=request.user,
                name=name,
                email=email,
                phone_number=phone_number,
                description=description,
                street_number=street_number,
                street_name=street_name,
                street_block=street_block,
                city=city,
                postal_code=postal_code,
                price_min=float(price_min) if price_min else 0,
                price_max=float(price_max) if price_max else 0,
                max_guest_count=int(max_guest_count) if max_guest_count else 0,
                opening_time=opening_time if opening_time else None,
                closing_time=closing_time if closing_time else None,
                operating_days=operating_days,
                custom_tags=custom_tags,
                status='PENDING'
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                file_path = f"restaurant_requests/images/{uuid.uuid4()}_{image_file.name}"
                image_url = upload_to_supabase(image_file, "files", file_path)
                if image_url:
                    restaurant_request.image = image_url
                    restaurant_request.save()
            
            # Handle proof of ownership upload
            if 'proof_of_ownership' in request.FILES:
                proof_file = request.FILES['proof_of_ownership']
                file_path = f"restaurant_requests/proofs/{uuid.uuid4()}_{proof_file.name}"
                proof_url = upload_to_supabase(proof_file, "files", file_path)
                if proof_url:
                    restaurant_request.proof_of_ownership = proof_url
                    restaurant_request.save()
            
            # Store cuisine IDs and tag IDs for later use when request is approved
            cuisine_ids = request.POST.getlist('cuisines')
            tag_ids = request.POST.getlist('tags')
            
            # Store these as JSON in a text field (we'll parse them when creating the restaurant)
            import json
            restaurant_request.admin_notes = json.dumps({
                'cuisine_ids': cuisine_ids,
                'tag_ids': tag_ids
            })
            restaurant_request.save()
            
            messages.success(request, f'Restaurant creation request for "{restaurant_request.name}" has been submitted! You will be notified once it\'s reviewed by an admin.')
            return redirect('manage_restaurant:list')
            
        except Exception as e:
            messages.error(request, f'Error submitting restaurant request: {str(e)}')
            return render(request, 'manage_restaurant/create_restaurant.html', {
                'cuisines': Cuisine.objects.all(),
                'tags': Tags.objects.all()
            })
    
    # GET request - show form
    return render(request, 'manage_restaurant/create_restaurant.html', {
        'cuisines': Cuisine.objects.all(),
        'tags': Tags.objects.all()
    })

@restaurant_login_required
@require_POST
def add_tag(request):
    """Create a new tag - only for owners"""
    if request.user.role != 'OWNER':
        return JsonResponse({'success': False, 'message': 'Only restaurant owners can create tags.'}, status=403)
    
    tag_name = request.POST.get('tag_name', '').strip()
    
    if not tag_name:
        return JsonResponse({'success': False, 'message': 'Tag name is required.'}, status=400)
    
    if len(tag_name) > 50:
        return JsonResponse({'success': False, 'message': 'Tag name must be 50 characters or less.'}, status=400)
    
    # Check if tag already exists (case-insensitive)
    existing_tag = Tags.objects.filter(tag__iexact=tag_name).first()
    if existing_tag:
        return JsonResponse({
            'success': True, 
            'tag': {'id': existing_tag.id, 'name': existing_tag.tag},
            'message': 'Tag already exists.'
        })
    
    # Create new tag
    try:
        new_tag = Tags.objects.create(tag=tag_name)
        return JsonResponse({
            'success': True,
            'tag': {'id': new_tag.id, 'name': new_tag.tag},
            'message': 'Tag created successfully!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating tag: {str(e)}'}, status=500)

@restaurant_login_required
def manage_reservations(request, restaurant_id):
    user = request.user
    if user.role == 'OWNER':
        owner = get_object_or_404(Owner, user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=owner)
    elif user.role == 'HOST':
        host = get_object_or_404(Host, user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, hosts=host)
    elif user.role == 'MANAGER':
        manager = get_object_or_404(Manager, user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, managers=manager)

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
                customer_name = reservation.customer.user.first_name if reservation.customer and reservation.customer.user else reservation.name
                messages.success(request, f"Confirmation email to {customer_name} has been sent")
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
                customer_name = reservation.customer.user.first_name if reservation.customer and reservation.customer.user else reservation.name
                messages.success(request, f"Thank you email to {customer_name} has been sent")
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
            if send_reservation_cancellation_email(reservation):
                customer_name = reservation.customer.user.first_name if reservation.customer and reservation.customer.user else reservation.name
                messages.success(request, f"Cancellation email to {customer_name} has been sent")
            reservation.delete()
        return redirect('manage_restaurant:reservations', restaurant_id=restaurant_id)
    
    # Handle CSV export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="reservations_{restaurant_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['#', 'Name', 'Email', 'Date', 'Time', 'Guests', 'Tables', 'Status', 'Notes', 'Created At'])
        
        for idx, reservation in enumerate(reservations, 1):
            email = reservation.customer.user.email if reservation.customer and reservation.customer.user else reservation.email
            tables_str = ', '.join(reservation.table_numbers) if reservation.table_numbers else 'Not assigned'
            writer.writerow([
                idx,
                reservation.name,
                email,
                reservation.date,
                reservation.time,
                reservation.guest_count,
                tables_str,
                reservation.status,
                reservation.notes or '',
                reservation.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    context = {
        "restaurant": restaurant.to_dict(),
        "restaurant_id": restaurant_id,
        "reservations": [r.to_dict() for r in reservations],
        "has_reservations": reservations.exists(),
        'floorplan': json.dumps(floorplan.to_dict()),
        "tables": json.dumps([t.to_dict() for t in tables]),
        "elements": json.dumps([e.to_dict() for e in elements])
    }
    return render(request, "manage_restaurant/manage_reservation.html", context)

@restaurant_login_required
def manage_tables(request, restaurant_id):
    user = request.user
    if user.role == 'OWNER':
        owner = get_object_or_404(Owner, user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=owner)
    elif user.role == 'MANAGER':
        manager = get_object_or_404(Manager, user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, managers=manager)

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

@restaurant_login_required
def manage_staffs(request, restaurant_id):
    user = request.user

    # Get the restaurant based on the user's role
    if user.role == 'OWNER':
        owner = get_object_or_404(Owner, user=user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=owner)
    elif user.role == 'MANAGER':
        manager = get_object_or_404(Manager, user=user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, managers=manager)

    # Handle POST request for sending staff invitations
    if request.method == 'POST':
        role = request.POST.get('role')
        email = request.POST.get('email')
        if role and email:
            try:
                from email_service.views import send_staff_invitation_email_u_e
                invited_user = User.objects.get(email=email, email_verified=True)
                if send_staff_invitation_email_u_e(invited_user, restaurant, role, request):
                    messages.success(request, "The staff invitation has been sent. They can now check their email to continue.")
                else:
                    messages.error(request, "The staff invitation has not been sent.")
            except User.DoesNotExist:
                from email_service.views import send_staff_invitation_email_u_d_n_e
                if send_staff_invitation_email_u_d_n_e(restaurant, email, role, request):
                    messages.success(request, "The staff invitation has been sent. They can now check their email to continue.")
                else:
                    messages.error(request, "The staff invitation has not been sent.")

    # Prepare the staff members list
    staff_members = []

    for host in restaurant.hosts.all():
        staff_members.append({
            'id': host.id,
            'name': host.user.get_full_name(),
            'email': host.user.email,
            'role': 'Host',
            'joined_at': host.user.date_joined,
            'is_current_user': host.user == user
        })

    for manager in restaurant.managers.all():
        staff_members.append({
            'id': manager.id,
            'name': manager.user.get_full_name(),
            'email': manager.user.email,
            'role': 'Manager',
            'joined_at': manager.user.date_joined,
            'is_current_user': manager.user == user
        })

    staff_members.sort(key=lambda x: (not x['is_current_user'], x['name']))

    context = {
        'staff': staff_members,
    }

    return render(request, "manage_restaurant/manage_staffs.html", context)

@restaurant_login_required
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
            
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                file_path = f"restaurants/{uuid.uuid4()}_{image_file.name}"
                image_url = upload_to_supabase(image_file, "files", file_path)
                if image_url:
                    restaurant.image = image_url
                else:
                    messages.warning(request, 'Failed to upload image. Restaurant details updated without image.')
            
            restaurant.save()
            messages.success(request, 'Restaurant details updated successfully!')
            return redirect('manage_restaurant:details', restaurant_id=restaurant_id)
        
        except Exception as e:
            messages.error(request, f'Error updating restaurant details: {str(e)}')
    
    context = {
        "restaurant": restaurant.to_dict(),
    }
    return render(request, "manage_restaurant/manage_details.html", context)

@restaurant_login_required
def dashboard(request, restaurant_id):
    user = request.user
    if user.role == 'OWNER':
        owner = get_object_or_404(Owner, user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=owner)
    elif user.role == 'HOST':
        host = get_object_or_404(Host, user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, hosts=host)
    elif user.role == 'MANAGER':
        manager = get_object_or_404(Manager, user=request.user)
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, managers=manager)
    # Get statistics
    total_reservations = Reservation.objects.filter(restaurant=restaurant).count()
    pending_reservations = Reservation.objects.filter(restaurant=restaurant, status='PENDING').count()
    confirmed_reservations = Reservation.objects.filter(restaurant=restaurant, status='CONFIRMED').count()
    total_tables = Table.objects.filter(floorplan=restaurant.floorplan).count()
    
    context = {
        "role": user.role,
        "restaurant": restaurant.to_dict(),
        "total_reservations": total_reservations,
        "pending_reservations": pending_reservations,
        "confirmed_reservations": confirmed_reservations,
        "total_tables": total_tables,
    }
    return render(request, "manage_restaurant/dashboard.html", context)