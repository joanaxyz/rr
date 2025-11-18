from django.shortcuts import render
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
            return render(request, "owner_verification/register_restaurant.html")

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
        messages.success(request, "Your request has been sent!")

    return render(request, "owner_verification/register_restaurant.html")