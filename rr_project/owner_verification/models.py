from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

User = settings.AUTH_USER_MODEL

class Owner(models.Model):
    GOVERNMENT_ID_CHOICES = [
        ("DL", "Driver’s License"),
        ("PP", "Passport"),
        ("NID", "National ID"),
        ("OTH", "Other"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUBMITTED", "Submitted"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="owner_verification_profile")

    govt_full_name = models.CharField(max_length=255)
    government_id_type = models.CharField(max_length=10, choices=GOVERNMENT_ID_CHOICES)
    government_id_number = models.CharField(max_length=100)
    business_address = models.TextField()
    business_email = models.EmailField(blank=True, null=True)

    business_license = models.FileField(
        upload_to="owner_docs/",
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
        blank=True,
        null=True,
    )
    government_id_front = models.FileField(
        upload_to="owner_docs/",
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
        blank=True,
        null=True,
    )
    government_id_back = models.FileField(
        upload_to="owner_docs/",
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
        blank=True,
        null=True,
    )
    proof_of_ownership = models.FileField(
        upload_to="owner_docs/",
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
        blank=True,
        null=True,
    )

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # If no business email is provided, use the user's email
        if not self.business_email and hasattr(self.user, "email"):
            self.business_email = self.user.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.govt_full_name}"
