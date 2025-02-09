from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date



class Venue(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(default='Unknown')
    city = models.CharField(max_length=100, default='Unknown', db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    amenities = models.JSONField(null=True, blank=False)
    availability = models.JSONField(default=list)  # Store list of dates as JSON strings
    image = models.ImageField(upload_to='venue_images/', null=True, blank=True, default='default_venue.jpg')
    rating = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    base_price = models.IntegerField(default=0)
    extra_guest_price = models.IntegerField(default=0)
    amenities_price = models.JSONField(default=dict)

    def clean(self):
        """Ensure availability stores dates as strings in ISO format."""
        if isinstance(self.availability, list):
            self.availability = [d.isoformat() if isinstance(d, date) else d for d in self.availability]

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




class PricingRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    event_date = models.DateField()
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pricing Request from {self.first_name} {self.last_name} for {self.venue.name if self.venue else 'Deleted Venue'}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    booking_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')

class Review(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review_text = models.TextField()

class SellerEarnings(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

