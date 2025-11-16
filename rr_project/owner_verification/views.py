from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import OwnerVerificationRequest

@login_required
def owner_verification(request):
    # if the user already submitted a request, show status
    existing_request = OwnerVerificationRequest.objects.filter(user=request.user).first()

    if existing_request:
        return render(request, "owner_verification/request_status.html", {
            "request_obj": existing_request
        })

    if request.method == "POST":

        # Get text fields from POST
        gov_full_name = request.POST.get("govt_full_name")
        id_type = request.POST.get("id_type")
        id_number = request.POST.get("id_number")
        business_address = request.POST.get("business_address")
        business_email = request.POST.get("business_email")
        tax_id = request.POST.get("tax_id")

        # Get uploaded files
        business_license = request.FILES.get("business_license")
        government_id_doc = request.FILES.get("government_id_doc")
        proof_ownership = request.FILES.get("proof_ownership")

        # Create verification request
        req = OwnerVerificationRequest.objects.create(
            user=request.user,
            gov_full_name=gov_full_name,
            id_type=id_type,
            id_number=id_number,
            business_address=business_address,
            business_email=business_email,
            tax_id=tax_id,
            business_license=business_license,
            government_id_doc=government_id_doc,
            proof_ownership=proof_ownership,
            state="PENDING",
        )

        req.save()

        return render(request, "owner_verification/success.html")

    return render(request, "owner_verification/register_restaurant.html")
def owner_requests(request):
    if not request.user.is_staff:  # Only admin/staff can see this
        return redirect('home')

    requests = OwnerVerificationRequest.objects.all()
    return render(request, 'owner_verification/list.html', {'requests': requests})

def update_request_status(request, pk, new_status):
    if not request.user.is_staff:
        return redirect('home')

    verification = get_object_or_404(OwnerVerificationRequest, pk=pk)
    if new_status in ['approved', 'not_approved']:
        verification.status = new_status
        verification.save()
    return redirect('owner_verification:owner_requests')