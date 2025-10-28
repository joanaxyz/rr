# urls.py
from django.urls import path
from .views import auth
from .views import restaurant
from .views.restaurant import api_save_layout, api_load_layout


app_name = 'rr_app'

urlpatterns = [
    # Authentication URLs
    path('auth/signup/', auth.signup_view, name='signup'),
    path('auth/login/', auth.login_view, name='login'),
    path('auth/logout/', auth.logout_view, name='logout'),
    
    # Email Verification URLs
    path('auth/verify-email/<uuid:token>/', auth.verify_email_view, name='verify_email'),
    path('auth/resend-verification/<int:user_id>/', auth.resend_verification_email_view, name='resend_verification'),
    
    # Forgot Password URLs (Custom implementation)
    path('auth/forgot-password/', auth.forgot_password_view, name='forgot_password'),
    path('auth/verify-reset-code/', auth.verify_reset_code_view, name='verify_reset_code'),
    path('auth/reset-password/', auth.reset_password_view, name='reset_password'),
    path('auth/resend-reset-code/', auth.resend_reset_code_view, name='resend_reset_code'),
    
    # Main application URLs
    path('dashboard/', restaurant.dashboard_view, name='dashboard'),
    path('restaurants/', restaurant.restaurants_view, name='restaurants'),
    path('reservation/manage/', restaurant.reservation_management_view, name='reservation_management'),
    path('restaurant/<int:restaurant_id>/', restaurant.restaurant_detail_view, name='restaurant_detail'),
    
    # Redirect root to login
    path('', auth.login_view, name='home'),

    # Admin restaurant layout URL
   path("dashboard/restaurant/<int:restaurant_id>/layout/", restaurant.admin_restaurant_layout, name="admin_restaurant_layout"),
     path('api/save-layout/<int:restaurant_id>/', api_save_layout, name='api_save_layout'),
    path('api/load-layout/<int:restaurant_id>/', api_load_layout, name='api_load_layout'),
]