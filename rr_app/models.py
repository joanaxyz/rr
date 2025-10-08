# models.py
from django.db import models
from django.utils import timezone
import uuid


class User(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    supabase_id = models.UUIDField(unique=True, help_text="Supabase User ID")
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    date_made = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    avatar_url = models.URLField(blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_made']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def update_last_login(self):
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

