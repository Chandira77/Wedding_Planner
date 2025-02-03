from django.db import models
from django.contrib.auth.models import User

class AvailableDate(models.Model):
    date = models.DateField()

    def __str__(self):
        return self.date.strftime('%Y-%m-%d')

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
   

    def __str__(self):
        return self.user.username



class Venue(models.Model):
    VENUE_TYPE_CHOICES = [
        ('temple', 'Temple'),
        ('hotel', 'Hotel'),
        ('banquet', 'Banquet'),
        ('church', 'Church'),
    ]
    
    name = models.CharField(max_length=255)
    venue_type = models.CharField(max_length=50, choices=VENUE_TYPE_CHOICES)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    amenities = models.ManyToManyField('Amenity', related_name='venues', blank=True)
    available_dates = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    capacity_min = models.IntegerField()
    capacity_max = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='venues/')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    

