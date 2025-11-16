from django.urls import path
from . import views

app_name = 'owner_verification'

urlpatterns = [
    # Mu submit ag owner sa verification form
    path('', views.owner_verification, name='owner_verification'),

    # Admin view: lista tanan owner verification requests
    path('requests/', views.owner_requests, name='owner_requests'),

    # Admin action: approve or not approve
    path('requests/<int:pk>/<str:new_status>/', views.update_request_status, name='update_request_status'),
]
