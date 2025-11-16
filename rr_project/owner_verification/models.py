from django.db import models
from django.conf import settings

class OwnerVerificationRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('NOT_APPROVED', 'Not Approved'),
    ]

    # Link to user model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner_requests')

    gov_full_name = models.CharField(max_length=255)
    id_type = models.CharField(max_length=50)
    id_number = models.CharField(max_length=100)
    business_address = models.CharField(max_length=255)
    business_email = models.EmailField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)

    # File uploads
    business_license = models.FileField(upload_to='owner_verification/licenses/')
    government_id_doc = models.FileField(upload_to='owner_verification/government_ids/')
    proof_ownership = models.FileField(upload_to='owner_verification/proofs/')

    # Request status
    state = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.state}"
