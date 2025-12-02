from django.urls import path
from django.views.generic import TemplateView
from . import views
from .api import (
    api_forgot_password,
    api_verify_reset_code,
    api_reset_password,
    api_resend_reset_code,
    api_resend_verification_email
)

app_name = 'accounts'

urlpatterns = [
    # Page URLs
    path('auth/register/', views.register_view, name='register'),
    path('auth/register/<str:email>/<str:role>/<int:restaurant_id>/', views.register_staff_view, name='register_staff'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),

    # Email Verification URLs
    path('auth/verify-email/<uuid:token>/', views.verify_email_view, name='verify_email'),
    path('auth/verify-email/<uuid:token>/<int:restaurant_id>/', views.verify_staff_email_view, name='verify_staff_email'),
    path('auth/resend-verification/<int:user_id>/', views.resend_verification_email_view, name='resend_verification'),

    # Forgot Password URLs
    path('auth/forgot-password/', views.forgot_password_view, name='forgot_password'),

    # Staff invitation URLs
    path('auth/invite-staff/<int:user_id>/<str:role>/<int:restaurant_id>/', views.invite_staff, name='invite_staff'),

    # Profile URL
    path('profile/', views.profile_view, name='profile'),
    
    # Delete Account URL
    path('delete-account/', views.delete_account_view, name='delete_account'),
    
    # API URLs
    path('api/forgot-password/', api_forgot_password, name='api_forgot_password'),
    path('api/verify-reset-code/', api_verify_reset_code, name='api_verify_reset_code'),
    path('api/reset-password/', api_reset_password, name='api_reset_password'),
    path('api/resend-reset-code/', api_resend_reset_code, name='api_resend_reset_code'),
    path('api/resend-verification/<int:user_id>/', api_resend_verification_email, name='api_resend_verification'),
]
