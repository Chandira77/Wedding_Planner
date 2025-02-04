from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Venue(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)  # Seller who added the venue
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    amenities = models.TextField()  # List of amenities as text
    availability = models.DateField(default=timezone.now)  # Available dates
    photo = models.ImageField(upload_to='venues/')  # Venue image upload

    def __str__(self):
        return self.name

    

