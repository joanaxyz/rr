from django.contrib import admin
from .models import Reservation, TableReservation
# Register your models here.

admin.site.register(Reservation)
admin.site.register(TableReservation)