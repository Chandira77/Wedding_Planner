from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Venue(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)  # Seller who added the venue
    name = models.CharField(max_length=255)
    description = models.TextField(default='Unknown')
    city = models.CharField(max_length=100, default='Unknown')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    amenities = models.TextField()  # List of amenities as text
    availability = models.DateField(default=timezone.now)  # Available dates
    image = models.ImageField(upload_to='venue_images/', null=True, blank=True)
    rating = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=[('Available', 'Available'), ('Unavailable', 'Unavailable')], default='Available')

    def __str__(self):
        return self.name


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

