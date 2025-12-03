from django.db import models
from accounts.models import User

class BusinessApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('NOT_APPROVED', 'Not Approved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_applications')

    govt_full_name = models.CharField(max_length=255)
    government_id_type = models.CharField(max_length=50)
    government_id_number = models.CharField(max_length=100)
    business_address = models.CharField(max_length=255)
    business_email = models.EmailField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)

    business_license = models.URLField(blank=True, null=True)
    government_id_front = models.URLField(blank=True, null=True)
    government_id_back = models.URLField(blank=True, null=True)
    proof_of_ownership = models.URLField(blank=True, null=True)

    state = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'owner_verification_ownerverificationrequest'  # Keep existing table name

    def __str__(self):
        return f"{self.user.username} - {self.state}"
