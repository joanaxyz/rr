from django.urls import path
from . import views

app_name = 'owner_verification'

urlpatterns = [
    path('', views.owner_verification, name='owner_verification'),

]
