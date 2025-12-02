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

    # Restaurant Information (optional - for creating restaurant upon acceptance)
    restaurant_name = models.CharField(max_length=100, blank=True, null=True)
    restaurant_phone = models.CharField(max_length=20, blank=True, null=True)
    restaurant_description = models.TextField(blank=True, null=True)
    
    # Restaurant Address components
    restaurant_street_number = models.CharField(max_length=50, blank=True, null=True)
    restaurant_street_name = models.CharField(max_length=100, blank=True, null=True)
    restaurant_street_block = models.CharField(max_length=100, blank=True, null=True)
    restaurant_city = models.CharField(max_length=100, blank=True, null=True)
    restaurant_postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Restaurant Operating Information
    restaurant_price_min = models.DecimalField(max_digits=8, decimal_places=2, default=0, blank=True, null=True)
    restaurant_price_max = models.DecimalField(max_digits=8, decimal_places=2, default=0, blank=True, null=True)
    restaurant_max_guests = models.IntegerField(blank=True, null=True)
    restaurant_opening_time = models.TimeField(null=True, blank=True)
    restaurant_closing_time = models.TimeField(null=True, blank=True)
    restaurant_operating_days = models.CharField(max_length=100, default='Mon,Tue,Wed,Thu,Fri,Sat,Sun', blank=True, null=True)
    restaurant_image = models.URLField(blank=True, null=True, help_text="URL to restaurant image stored in Supabase")

    state = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'owner_verification_ownerverificationrequest'  # Keep existing table name

    def __str__(self):
        return f"{self.user.username} - {self.state}"
