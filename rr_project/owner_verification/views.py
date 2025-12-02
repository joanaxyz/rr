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

        if not all([govt_full_name, government_id_type, government_id_number, business_address, tax_id]):
            messages.error(request, "All fields are required.")
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