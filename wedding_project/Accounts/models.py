from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    BUSINESS_CATEGORIES = [
        ('decoration', 'Decoration'),
        ('catering', 'Catering'),
        ('photography', 'Photography'),
        ('videography', 'Videography'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
        ('guest', 'Guest')
    ], default='user')
    business_category = models.CharField(max_length=50, choices=BUSINESS_CATEGORIES, blank=True, null=True)  # New field

    def __str__(self):
        return f"{self.user.username} ({self.role})"
