from django.db import models
from django.conf import settings

class Restaurant(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    seats = models.PositiveIntegerField()

class Reservation(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
