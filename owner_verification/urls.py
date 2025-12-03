from django.urls import path
from . import views

app_name = 'business'

urlpatterns = [
    path('apply/', views.apply_business, name='apply'),
]
