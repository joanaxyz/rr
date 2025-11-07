from django.db import models
from django.contrib.postgres.fields import ArrayField
from restaurants.models import Restaurant, Table
from accounts.models import Customer
from django.utils.timezone import localtime

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
    cancellation_info = models.JSONField(blank=True, null=True, default=dict)
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='reservations',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        restaurant_name = self.restaurant.name if self.restaurant else 'Unknown Restaurant'
        return f"{self.name} - {self.guest_count} guests at {restaurant_name} on {self.date} at {self.time} [{self.status}]"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "guest_count": self.guest_count,
            "date": self.date.isoformat() if self.date else None,
            "time": self.time.strftime("%H:%M:%S") if self.time else None,
            "notes": self.notes or "",
            "table_numbers": list(self.table_numbers or []),
            "status": self.status,
            "cancellation_info":{
                'reason': self.cancellation_info.get('reason') if self.cancellation_info else None,
                'sender': self.cancellation_info.get('sender') if self.cancellation_info else None
            },
            "restaurant": self.restaurant.name if self.restaurant else None,
            "restaurant_id": self.restaurant.id if self.restaurant else None,
            "customer": {
                "id": self.customer.id,
                "name": getattr(self.customer, "name", None),
                "email": getattr(self.customer, "email", None)
            } if self.customer else None,
            "created_at": localtime(self.created_at).isoformat() if self.created_at else None
        }
    
class TableReservation(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
