from django.urls import path
from . import views, auth_views

app_name = 'admin_panel'

urlpatterns = [
    path('auth/login/', auth_views.admin_login_view, name='login'),
    path('auth/logout/', auth_views.admin_logout_view, name='logout'),
    
    path('', views.dashboard, name='dashboard'),
    path('admins/', views.manage_admins, name='manage_admins'),
    path('owner-requests/', views.owner_verification_requests, name='owner_verification_requests'),
    path('restaurant-requests/', views.restaurant_creation_requests, name='restaurant_creation_requests'),
    
    # User Management
    path('users/', views.users, name='users'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/export/', views.export_users_csv, name='export_users_csv'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
    # Restaurant Management
    path('restaurants/', views.restaurants, name='restaurants'),
    path('restaurants/create/', views.restaurant_create, name='restaurant_create'),
    path('restaurants/export/', views.export_restaurants_csv, name='export_restaurants_csv'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurants/<int:restaurant_id>/edit/', views.restaurant_edit, name='restaurant_edit'),
    path('restaurants/<int:restaurant_id>/delete/', views.restaurant_delete, name='restaurant_delete'),
    
    # Reservation Management
    path('reservations/', views.reservations, name='reservations'),
    path('reservations/create/', views.reservation_create, name='reservation_create'),
    path('reservations/export/', views.export_reservations_csv, name='export_reservations_csv'),
    path('reservations/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:reservation_id>/edit/', views.reservation_edit, name='reservation_edit'),
    path('reservations/<int:reservation_id>/delete/', views.reservation_delete, name='reservation_delete'),
    
    # Review Management
    path('reviews/', views.reviews, name='reviews'),
    path('reviews/create/', views.review_create, name='review_create'),
    path('reviews/export/', views.export_reviews_csv, name='export_reviews_csv'),
    path('reviews/<int:review_id>/', views.review_detail, name='review_detail'),
    path('reviews/<int:review_id>/edit/', views.review_edit, name='review_edit'),
    path('reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),
    
    # Cuisine Management
    path('cuisines/', views.cuisines, name='cuisines'),
    path('cuisines/create/', views.cuisine_create, name='cuisine_create'),
    path('cuisines/<int:cuisine_id>/edit/', views.cuisine_edit, name='cuisine_edit'),
    path('cuisines/<int:cuisine_id>/delete/', views.cuisine_delete, name='cuisine_delete'),
    
    # Tag Management
    path('tags/', views.tags, name='tags'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:tag_id>/edit/', views.tag_edit, name='tag_edit'),
    path('tags/<int:tag_id>/delete/', views.tag_delete, name='tag_delete'),
]
