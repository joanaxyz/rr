from django.db import models
from django.contrib.postgres.fields import ArrayField
from restaurants.models import Restaurant
from accounts.models import Customer

class Reservation(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='reservations',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    guest_count = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    table_numbers = ArrayField(
        models.CharField(),
        blank=True,
        default=list
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('CANCELLED', 'Cancelled'),
            ('COMPLETED', 'Completed'),
        ],
        default='PENDING'
    )
    cancellation_reason = models.TextField(blank=True, null=True)
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='reservations',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)
    previous_status = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        restaurant_name = self.restaurant.name if self.restaurant else 'Unknown Restaurant'
        return f"{self.name} - {self.guest_count} guests at {restaurant_name} on {self.date} at {self.time} [{self.status}]"
