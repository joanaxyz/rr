from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import OwnerVerificationRequest
from .supabase_utils import upload_to_supabase
import uuid

@login_required
def owner_verification(request):
    if request.method == "POST":
        govt_full_name = request.POST.get("govt_full_name")
        government_id_type = request.POST.get("government_id_type")
        government_id_number = request.POST.get("government_id_number")
        business_address = request.POST.get("business_address")
        business_email = request.POST.get("business_email") or request.user.email
        tax_id = request.POST.get("tax_id")

        business_license_file = request.FILES.get("business_license")
        government_id_front_file = request.FILES.get("government_id_front")
        government_id_back_file = request.FILES.get("government_id_back")
        proof_ownership_file = request.FILES.get("proof_ownership")

        # Restaurant information
        restaurant_name = request.POST.get("restaurant_name")
        restaurant_phone = request.POST.get("restaurant_phone")
        restaurant_description = request.POST.get("restaurant_description")
        restaurant_street_number = request.POST.get("restaurant_street_number", "")
        restaurant_street_name = request.POST.get("restaurant_street_name", "")
        restaurant_street_block = request.POST.get("restaurant_street_block", "")
        restaurant_city = request.POST.get("restaurant_city", "")
        restaurant_postal_code = request.POST.get("restaurant_postal_code", "")
        restaurant_price_min = request.POST.get("restaurant_price_min", 0)
        restaurant_price_max = request.POST.get("restaurant_price_max", 0)
        restaurant_max_guests = request.POST.get("restaurant_max_guests")
        restaurant_opening_time = request.POST.get("restaurant_opening_time")
        restaurant_closing_time = request.POST.get("restaurant_closing_time")
        restaurant_operating_days_list = request.POST.getlist("restaurant_operating_days")
        restaurant_image_file = request.FILES.get("restaurant_image")

        if not all([govt_full_name, government_id_type, government_id_number, business_address, tax_id]):
            messages.error(request, "All required fields are required.")
            return render(request, "owner_verification/apply_owner.html")

        # Validate restaurant fields if provided
        if restaurant_name and not all([restaurant_name, restaurant_phone, restaurant_description, restaurant_max_guests]):
            messages.error(request, "Please fill in all required restaurant fields.")
            return render(request, "owner_verification/apply_owner.html")

        req = OwnerVerificationRequest(
            user=request.user,
            govt_full_name=govt_full_name,
            government_id_type=government_id_type,
            government_id_number=government_id_number,
            business_address=business_address,
            business_email=business_email,
            tax_id=tax_id,
            state="PENDING"
        )

        # Save restaurant information if provided
        if restaurant_name:
            req.restaurant_name = restaurant_name
            req.restaurant_phone = restaurant_phone
            req.restaurant_description = restaurant_description
            req.restaurant_street_number = restaurant_street_number
            req.restaurant_street_name = restaurant_street_name
            req.restaurant_street_block = restaurant_street_block
            req.restaurant_city = restaurant_city
            req.restaurant_postal_code = restaurant_postal_code
            req.restaurant_price_min = float(restaurant_price_min) if restaurant_price_min else 0
            req.restaurant_price_max = float(restaurant_price_max) if restaurant_price_max else 0
            req.restaurant_max_guests = int(restaurant_max_guests) if restaurant_max_guests else None
            req.restaurant_opening_time = restaurant_opening_time if restaurant_opening_time else None
            req.restaurant_closing_time = restaurant_closing_time if restaurant_closing_time else None
            req.restaurant_operating_days = ",".join(restaurant_operating_days_list) if restaurant_operating_days_list else 'Mon,Tue,Wed,Thu,Fri,Sat,Sun'

        if business_license_file:
            file_path = f"owner_verification/licenses/{uuid.uuid4()}_{business_license_file.name}"
            req.business_license = upload_to_supabase(business_license_file, "files", file_path)

        if government_id_front_file:
            file_path = f"owner_verification/government_ids/{uuid.uuid4()}_{government_id_front_file.name}"
            req.government_id_front = upload_to_supabase(government_id_front_file, "files", file_path)

        if government_id_back_file:
            file_path = f"owner_verification/government_ids/{uuid.uuid4()}_{government_id_back_file.name}"
            req.government_id_back = upload_to_supabase(government_id_back_file, "files", file_path)

        if proof_ownership_file:
            file_path = f"owner_verification/proofs/{uuid.uuid4()}_{proof_ownership_file.name}"
            req.proof_of_ownership = upload_to_supabase(proof_ownership_file, "files", file_path)

        if restaurant_image_file:
            file_path = f"owner_verification/restaurant_images/{uuid.uuid4()}_{restaurant_image_file.name}"
            req.restaurant_image = upload_to_supabase(restaurant_image_file, "files", file_path)

        req.save()
        
        # Send notification email to admin (optional - can be implemented later)
        # For now, just notify the user
        site_url = request.build_absolute_uri('/')
        context = {
            'user': request.user,
            'site_url': site_url,
        }
        # Note: You might want to create an email template for request submission confirmation
        # send_email(
        #     subject='Owner Verification Request Submitted - RR',
        #     template_name='emails/owner_request_submitted.html',
        #     context=context,
        #     recipient_email=request.user.email
        # )
        
        messages.success(request, "Your request has been sent! You will be notified via email once it's reviewed.")
        return redirect('owner_verification:owner_verification')

    return render(request, "owner_verification/apply_owner.html")