    
from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    # Page URLS
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    
    # Email Verification URLs
    path('auth/verify-email/<uuid:token>/', verify_email_view, name='verify_email'),
    path('auth/resend-verification/<int:user_id>/', resend_verification_email_view, name='resend_verification'),
    
    # Forgot Password URLs (Custom implementation)
    path('auth/forgot-password/', forgot_password_view, name='forgot_password'),
    path('auth/verify-reset-code/', verify_reset_code_view, name='verify_reset_code'),
    path('auth/reset-password/', reset_password_view, name='reset_password'),
    path('auth/resend-reset-code/', resend_reset_code_view, name='resend_reset_code'),
]