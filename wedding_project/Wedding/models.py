from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now
from datetime import date
import json
import uuid
from django.urls import reverse
#from Wedding.models import Event


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
    amenities = models.JSONField(null=True, blank=False,default=dict)
    availability = models.JSONField(default=list)
    image = models.ImageField(upload_to='venue_images/', null=True, blank=True, default='default_venue.jpg')
    rating = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    base_price = models.IntegerField(default=0)
    extra_guest_price = models.IntegerField(default=0)
    amenities_price = models.JSONField(default=dict)

    def __str__(self):
        return self.name





class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=200, blank=True, null=True)  # New field
    profile_image = models.ImageField(upload_to='seller_profiles/', default='default.jpg')
    description = models.TextField(blank=True, null=True)  # New field
    services = models.TextField(blank=True, null=True)  # New field
    website = models.URLField(blank=True, null=True)  # New field
    average_rating = models.FloatField(default=0.0)  # New field
    is_seller = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # New field

    def __str__(self):
        return f"{self.user.username} - {self.business_category}"
    


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ServiceListing(models.Model):
    SERVICE_TYPES = [
        ('Catering', 'Catering'),
        ('Decoration', 'Decoration'),
        ('Photography', 'Photography'),
        ('Videography', 'Videography'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE) 
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="Unnamed Service")
    description = models.TextField(default="No description available")
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)  # Service category
    city = models.CharField(max_length=100)  # City
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')  # Status
    images = models.ImageField(upload_to='service_images/', blank=True, null=True)  # Image Upload
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    availability = models.DateField()  # Available date
    
    # Dynamic Pricing Fields
    base_price = models.DecimalField(max_digits=10, decimal_places=2)  # Base price
    extra_guest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Extra guest charge per head
    amenities_price = models.JSONField(default=dict, blank=True)  # Stores amenities pricing in JSON format

    def get_amenities_price(self):
        """Return amenities as a dictionary"""
        return self.amenities_price if isinstance(self.amenities_price, dict) else json.loads(self.amenities_price)

    def calculate_total_price(self, guests=0, selected_amenities=[]):
        """Calculate total price based on guests and selected amenities"""
        total = self.base_price + (guests * self.extra_guest_price)
        for amenity in selected_amenities:
            total += self.get_amenities_price().get(amenity, 0)
        return total

    def __str__(self):
        return f"{self.service_type} - {self.seller.username}"

class PricingRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Track which user made the request
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE) 
    seller_email = models.EmailField()  
    service_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    event_date = models.DateField()
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pricing Request from {self.user.username} for {self.service_name}"










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
    created_at = models.DateTimeField(default=now)  # ✅ Add timestamp

    def __str__(self):
        return f"{self.seller.username} Earnings"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return self.user.username


# class Event(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)  # The event creator
#     name = models.CharField(max_length=255)
#     date = models.DateField()
#     venue = models.CharField(max_length=255)

#     def __str__(self):
#         return self.name



class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    invite_link = models.CharField(max_length=255, blank=True, null=True)
    unique_token = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unique_token:
            self.unique_token = uuid.uuid4().hex[:10]
            self.invite_link = f"/rsvp/{self.unique_token}/"
        super().save(*args, **kwargs)

    def get_invite_link(self):
        return reverse('view_invitation', args=[self.unique_token])

    def __str__(self):
        return self.name



class Guest(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    category = models.CharField(
        max_length=20,
        choices=[('Family', 'Family'), ('Friends', 'Friends'), ('Colleagues', 'Colleagues'), ('VIP', 'VIP')]
    )
    assigned_side = models.CharField(max_length=10, choices=[('Bride', 'Bride'), ('Groom', 'Groom')])

    is_invited = models.BooleanField(default=False)
    is_attending = models.BooleanField(default=False)



    def __str__(self):
        return f"{self.name} - {self.event.name}"
    


class RSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rsvps")
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, blank=True, null=True)  # Guest optional garna milcha
    response = models.CharField(
        max_length=15,
        choices=[('Attending', 'Attending'), ('Not Attending', 'Not Attending'), ('Maybe', 'Maybe')],
        default='Maybe'
    )
    message = models.TextField(blank=True, null=True)  # Optional message from the guest
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RSVP - {self.event.name}: {self.response}"




class Seating(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    table_number = models.PositiveIntegerField()

class DietaryPreference(models.Model):
    guest = models.OneToOneField(Guest, on_delete=models.CASCADE)
    preference = models.CharField(
        max_length=20,
        choices=[('Veg', 'Veg'), ('Non-Veg', 'Non-Veg'), ('Gluten-Free', 'Gluten-Free')],
        default='Veg'
    )
    special_request = models.TextField(blank=True, null=True)


class CheckIn(models.Model):
    guest = models.OneToOneField(Guest, on_delete=models.CASCADE)
    checked_in = models.BooleanField(default=False)





class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email