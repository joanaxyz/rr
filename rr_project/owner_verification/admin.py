from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import OwnerVerificationRequest

@admin.register(OwnerVerificationRequest)
class OwnerVerificationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "govt_full_name",
        "government_id_type",
        "government_id_number",
        "business_address",
        "state",
        "created_at",
    )
    list_filter = ("state", "created_at")
    search_fields = ("user__username", "govt_full_name", "government_id_number", "business_address")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    # Custom actions
    actions = ["accept_requests", "cancel_requests"]

    def accept_requests(self, request, queryset):
        for obj in queryset:
            if obj.state != "ACCEPTED":
                # Update state
                obj.state = "ACCEPTED"
                obj.save()

                # Assign the user role as OWNER
                user = obj.user
                if hasattr(user, 'profile'):  # if you have a profile model with role
                    user.profile.role = "OWNER"
                    user.profile.save()
                else:
                    # fallback: if you store role directly in user
                    user.role = "OWNER"
                    user.save()

                # Send confirmation email
                send_mail(
                    subject="Owner Verification Approved",
                    message=f"Hi {user.username},\n\nYour owner verification request has been APPROVED. You can now manage your restaurant.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
        self.message_user(request, "Selected requests have been ACCEPTED.")

    accept_requests.short_description = "Accept selected verification requests"

    def cancel_requests(self, request, queryset):
        for obj in queryset:
            if obj.state != "NOT_APPROVED":
                obj.state = "NOT_APPROVED"
                obj.save()

                # Send cancellation email
                user = obj.user
                send_mail(
                    subject="Owner Verification Not Approved",
                    message=f"Hi {user.username},\n\nYour owner verification request has been NOT APPROVED by admin.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
        self.message_user(request, "Selected requests have been NOT APPROVED.")

    cancel_requests.short_description = "Cancel selected verification requests"
