from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import Customer, Owner

class Floorplan(models.Model):
    width = models.IntegerField(default=800, help_text="Floor plan canvas width in pixels")
    height = models.IntegerField(default=500, help_text="Floor plan canvas height in pixels")
    restaurant = models.OneToOneField(
        'Restaurant',
        on_delete=models.CASCADE,
        related_name='floorplan',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Floorplan {self.id} ({self.width}x{self.height})"
    
    def to_dict(self):
        return {
            "id": self.id,
            "width": self.width,
            "height": self.height,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    # Separated address components
    city = models.CharField(max_length=100, blank=True, null=True, help_text="City name")
    street_block = models.CharField(max_length=100, blank=True, null=True, help_text="Block or District")
    street_name = models.CharField(max_length=100, blank=True, null=True, help_text="Street name")
    street_number = models.CharField(max_length=50, blank=True, null=True, help_text="Building/House number")
    postal_code = models.CharField(max_length=20, blank=True, null=True, help_text="Postal code")
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    owner = models.ForeignKey(
        Owner,
        related_name='restaurant',
        on_delete=models.SET_NULL,
        null=True
    )
    customers = models.ManyToManyField(
        Customer,
        related_name='restaurants',
        blank=True
    )
    price_min = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Minimum food price")
    price_max = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Maximum food price")
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    description = models.TextField()
    max_guest_count = models.IntegerField()
    opening_time = models.TimeField(null=True, blank=True, help_text="Restaurant opening time")
    closing_time = models.TimeField(null=True, blank=True, help_text="Restaurant closing time")
    operating_days = models.CharField(max_length=100, default='Mon,Tue,Wed,Thu,Fri,Sat,Sun', help_text="Comma-separated list of operating days (e.g., Mon,Tue,Wed,Thu,Fri,Sat,Sun)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    @property
    def full_address(self):
        """Generate full address from components"""
        parts = []
        if self.street_number:
            parts.append(self.street_number)
        if self.street_name:
            parts.append(self.street_name)
        if self.street_block:
            parts.append(self.street_block)
        if self.city:
            parts.append(self.city)
        if self.postal_code:
            parts.append(self.postal_code)
        return ", ".join(parts) if parts else "Address not available"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.full_address,
            "phone_number": self.phone_number,
            "email": self.email,
            "description": self.description,
            "price_range_display": self.price_range_display,
            "is_open_now": self.is_open_now,
            "opening_time": self.opening_time.strftime("%I:%M %p") if self.opening_time else None,
            "closing_time": self.closing_time.strftime("%I:%M %p") if self.closing_time else None,
            "avg_rating": getattr(self, "avg_rating", 0),
            "review_count": getattr(self, "review_count", 0),
            "image": self.image.url if self.image else None,
            "cuisines": [{"name": c.name, "id": c.id} for c in self.cuisines.all()],
            "tags": [{"tag": t.tag, "id": t.id} for t in self.tags.all()],
            "operating_days": self.operating_days,
            "max_guest_count": self.max_guest_count,
        }
    
    @property
    def is_open_now(self):
        """Check if restaurant is currently open"""
        if not self.opening_time or not self.closing_time:
            return False
        
        current_time = timezone.now().time()
        
        # Handle cases where restaurant closes after midnight
        if self.closing_time < self.opening_time:
            # e.g., opens at 18:00, closes at 02:00 next day
            return current_time >= self.opening_time or current_time <= self.closing_time
        else:
            # Normal case: opens and closes on same day
            return self.opening_time <= current_time <= self.closing_time
    @property
    def is_open_on_date(self, date):
        # Get the day of the week for the date (0=Monday, 6=Sunday)
        weekday = date.weekday()
        
        # Map weekday to a short name (Mon, Tue, etc.)
        weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_name = weekday_names[weekday]
        
        # Check if the operating_days field contains the current day
        return day_name in self.operating_days.split(',')
    @property
    def price_range_display(self):
        """Return formatted food price range for display"""
        if self.price_min and self.price_max:
            return f"₱{int(self.price_min)} - ₱{int(self.price_max)}"
        return "Price not available"

class Element(models.Model):
    name = models.CharField(max_length = 50)
    x = models.DecimalField(max_digits=10, decimal_places=2)
    y = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    floorplan = models.ForeignKey(
        Floorplan,
        on_delete=models.CASCADE,
        related_name='elements',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "x": float(self.x),
            "y": float(self.y),
            "width": float(self.width),
            "height": float(self.height),
            "floorplan_id": self.floorplan_id,
            "created_at": self.created_at.isoformat()
        }
class Table(models.Model):
    number = models.IntegerField()
    capacity = models.IntegerField()
    x = models.DecimalField(max_digits=10, decimal_places=2)
    y = models.DecimalField(max_digits=10, decimal_places=2)
    TABLE_STATUS_CHOICES = [
        ('available', 'AVAILABLE'),
        ('reserved', 'RESERVED'),
        ('occupied', 'OCCUPIED'),
        ('cleaning', 'CLEANING'),
        ('unavailable', 'UNAVAILABLE'),
    ]
    floorplan = models.ForeignKey(
        Floorplan,
        on_delete=models.CASCADE,
        related_name='tables',
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=TABLE_STATUS_CHOICES,
        default='available'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.number
    
    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "capacity": self.capacity,
            "x": float(self.x),
            "y": float(self.y),
            "status": self.status,
            "floorplan_id": self.floorplan_id,
            "created_at": self.created_at.isoformat(),
        }

class Cuisine(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    restaurant = models.ManyToManyField(Restaurant,
                related_name="cuisines")
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class Review(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5.0)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating']
        
    def __str__(self):
        customer_name = self.customer.user.get_full_name() if self.customer else "Anonymous"
        return f'Review by {customer_name} for {self.restaurant.name}'
    
    def to_dict(self):
        customer_name = self.customer.user.get_full_name() if self.customer else "Anonymous"
        return {
            "id": self.id,
            "rating": float(self.rating),
            "comment": self.comment,
            "customer_name": customer_name,
            "created_at": self.created_at
        }


class Tags(models.Model):
    tag = models.CharField(max_length=50)
    restaurants = models.ManyToManyField(
        Restaurant,
        related_name='tags',
        blank=True
    )
    
    class Meta:
        ordering = ['tag']
        
    def __str__(self):
        return self.tag
    
    def to_dict(self):
        return {
            "id": self.id,
            "tag": self.tag,
        }