    
from django.urls import path
from .views import *
from .api import (
    api_forgot_password,
    api_verify_reset_code,
    api_reset_password,
    api_resend_reset_code,
    api_resend_verification_email
)

app_name = 'accounts'

urlpatterns = [
    # Page URLS
    path('auth/register/', register_view, name='register'),
    path('auth/register/<str:email>/<str:role>/<int:restaurant_id>', register_staff_view, name='register_staff'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    
    # Email Verification URLs
    path('auth/verify-email/<uuid:token>/', verify_email_view, name='verify_email'),
    path('auth/verify-email/<uuid:token>/<int:restaurant_id>/', verify_staff_email_view, name='verify_staff_email'),

    path('auth/resend-verification/<int:user_id>/', resend_verification_email_view, name='resend_verification'),
    
    # Forgot Password URLs (Custom implementation)
    path('auth/forgot-password/', forgot_password_view, name='forgot_password'),

    # Staff invitation URLS
    path('auth/invite-staff/<int:user_id>/<str:role>/<int:restaurant_id>', invite_staff, name='invite_staff'),
    
    # API URLs
    path('api/forgot-password/', api_forgot_password, name='api_forgot_password'),
    path('api/verify-reset-code/', api_verify_reset_code, name='api_verify_reset_code'),
    path('api/reset-password/', api_reset_password, name='api_reset_password'),
    path('api/resend-reset-code/', api_resend_reset_code, name='api_resend_reset_code'),
    path('api/resend-verification/<int:user_id>/', api_resend_verification_email, name='api_resend_verification'),
]