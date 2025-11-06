from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
import random
import string

# Create your models here.
class UserRole(models.TextChoices):
    CUSTOMER = 'CUSTOMER', 'Customer'
    OWNER = 'OWNER', 'Owner'
    HOST = 'Host', 'host'
    SERVER = 'Server', 'server'
    MANAGER = 'Manager', 'manager'


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER)
    banned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20, null=True)

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

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')

    def __str__(self):
        return f"Owner: {self.user.email or self.user.username}"
class Host(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='host_profile')

    def __str__(self):
        return f"Host: {self.user.email or self.user.username}"

class Server(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='server_profile')

    def __str__(self):
        return f"Server: {self.user.email or self.user.username}"

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')

    def __str__(self):
        return f"Manager: {self.user.email or self.user.username}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    def __str__(self):
        return f"Customer: {self.user.email or self.user.username}"