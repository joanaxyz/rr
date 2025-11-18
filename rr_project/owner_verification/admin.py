from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import OwnerVerificationRequest

admin.site.register(OwnerVerificationRequest)