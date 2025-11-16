from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import OwnerVerificationRequest  # Use the correct model

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=OwnerVerificationRequest)
def update_user_role(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        if hasattr(user, "role"):
            user.role = "OWNER"
            user.save(update_fields=["role"])
