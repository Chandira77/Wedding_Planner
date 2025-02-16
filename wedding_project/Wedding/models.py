from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date



class Venue(models.Model):
    CATEGORY_CHOICES = [
        ('venue', 'Venue'),
        ('catering', 'Catering'),
        ('decoration', 'Decoration'),
        ('photography', 'Photography'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(default='Unknown')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='venue')  # Added Category
    venue_type = models.CharField(max_length=100, choices=[  # Added Venue Type
        ('hotel', 'Hotel'),
        ('banquet', 'Banquet'),
        ('temple', 'Temple'),
        ('church', 'Church'),
    ], default='banquet')
    city = models.CharField(max_length=100, default='Unknown', db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    amenities = models.JSONField(null=True, blank=False)
    availability = models.JSONField(default=list)
    image = models.ImageField(upload_to='venue_images/', null=True, blank=True, default='default_venue.jpg')
    rating = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    base_price = models.IntegerField(default=0)
    extra_guest_price = models.IntegerField(default=0)
    amenities_price = models.JSONField(default=dict)

    def __str__(self):
        return self.name




class ServiceListing(models.Model):
    SERVICE_TYPES = [
        ('Catering', 'Catering'),
        ('Decoration', 'Decoration'),
        ('Photography', 'Photography'),
        ('Videography', 'Videography'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE)  # Seller info
    name = models.CharField(max_length=255, default="Unnamed Service")
    description = models.TextField(default="No description available")
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)  # Service category
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price
    availability = models.DateField()  # Available date
    amenities = models.TextField(blank=True, null=True)  # Additional features
    category = models.CharField(max_length=100)  # Service category
    city = models.CharField(max_length=100)  # City
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')  # Status
    images = models.ImageField(upload_to='service_images/', blank=True, null=True)  # Image Upload
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"{self.service_type} - {self.seller.username}"


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


class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    profile_image = models.ImageField(upload_to='seller_profiles/', default='default.jpg')
    is_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.business_name






class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    booking_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.venue.name}"




class Review(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review_text = models.TextField()

class SellerEarnings(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.seller.business_name} Earnings"
