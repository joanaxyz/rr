class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
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
    layout = models.JSONField(null=True, blank=True, default=list)
    opening_time = models.TimeField(null=True, blank=True, help_text="Restaurant opening time")
    closing_time = models.TimeField(null=True, blank=True, help_text="Restaurant closing time")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
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
        }

    @property
    def is_open_now(self):
        if not self.opening_time or not self.closing_time:
            return False
        current_time = timezone.now().time()
        if self.closing_time < self.opening_time:
            return current_time >= self.opening_time or current_time <= self.closing_time
        else:
            return self.opening_time <= current_time <= self.closing_time

    @property
    def price_range_display(self):
        """Return formatted food price range for display"""
        if self.price_min and self.price_max:
            return f"₱{int(self.price_min)} - ₱{int(self.price_max)}"
        return "Price not available"
