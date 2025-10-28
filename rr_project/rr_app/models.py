from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
import uuid
import random
import string   


### Users

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    CUSTOMER = 'CUSTOMER', 'Customer'


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER)
    banned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Email verification fields
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True)
    verification_token_expires = models.DateTimeField(null=True, blank=True)
    
    # Password reset fields
    password_reset_code = models.CharField(max_length=6, null=True, blank=True)
    password_reset_code_expires = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email or self.username
    
    def generate_verification_token(self):
        """Generate a new verification token that expires in 24 hours."""
        self.verification_token = uuid.uuid4()
        self.verification_token_expires = timezone.now() + timezone.timedelta(hours=24)
        self.save()
    
    def generate_password_reset_code(self):
        """Generate a new 6-digit password reset code that expires in 15 minutes."""
        self.password_reset_code = ''.join(random.choices(string.digits, k=6))
        self.password_reset_code_expires = timezone.now() + timezone.timedelta(minutes=15)
        self.save()
        return self.password_reset_code
    
    def is_password_reset_code_valid(self, code):
        """Check if the provided password reset code is valid and not expired."""
        if not self.password_reset_code or not self.password_reset_code_expires:
            return False
        return (self.password_reset_code == code and 
                self.password_reset_code_expires > timezone.now())
    
    def clear_password_reset_code(self):
        """Clear the password reset code after successful reset."""
        self.password_reset_code = None
        self.password_reset_code_expires = None
        self.save()


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')

    def __str__(self):
        return f"Admin: {self.user.email or self.user.username}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    def __str__(self):
        return f"Customer: {self.user.email or self.user.username}"


### Restaurants and Reservations

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    customers = models.ManyToManyField(
        Customer,
        related_name='restaurants',
        blank=True
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    description = models.TextField()
    max_guest_count = models.IntegerField()

    # ✅ NEW FIELD: JSON layout for storing table placements
    layout = models.JSONField(null=True, blank=True, default=list)

    opening_time = models.TimeField(null=True, blank=True, help_text="Restaurant opening time")
    closing_time = models.TimeField(null=True, blank=True, help_text="Restaurant closing time")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_open_now(self):
        if not self.opening_time or not self.closing_time:
            return False
        current_time = timezone.now().time()
        if self.closing_time < self.opening_time:
            return current_time >= self.opening_time or current_time <= self.closing_time
        else:
            return self.opening_time <= current_time <= self.closing_time
class Cuisine(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    restaurant = models.ManyToManyField(Restaurant,
                related_name="cuisines")
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Reservation(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='reservations',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    guest_count = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    table_numbers = ArrayField(
        models.CharField(),
        blank=True,
        default=list
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('CANCELLED', 'Cancelled'),
            ('COMPLETED', 'Completed'),
        ],
        default='PENDING'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='reservations',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        restaurant_name = self.restaurant.name if self.restaurant else 'Unknown Restaurant'
        return f"{self.name} - {self.guest_count} guests at {restaurant_name} on {self.date} at {self.time} [{self.status}]"


class Review(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5.0)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating']
        
    def __str__(self):
        customer_name = self.customer.user.get_full_name() if self.customer else "Anonymous"
        return f'Review by {customer_name} for {self.restaurant.name}'


class Tags(models.Model):
    tag = models.CharField(max_length=50)
    restaurants = models.ManyToManyField(
        Restaurant,
        related_name='tags',
        blank=True
    )
    
    class Meta:
        ordering = ['tag']
        
    def __str__(self):
        return self.tag