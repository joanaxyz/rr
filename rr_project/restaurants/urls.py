from django.urls import path
from .views import *

app_name = 'restaurants'

urlpatterns = [
    path('', restaurants_view, name='list'),
    path('<int:restaurant_id>/', restaurant_detail_view, name='detail'),
    path('<int:restaurant_id>/bookmark/', toggle_bookmark, name='toggle_bookmark'),
]