from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import SellerProfile

@receiver(post_save, sender=User)
def create_seller_profile(sender, instance, created, **kwargs):
    if created:  # Runs only when a new user is created
        if instance.is_staff:  # Assuming staff users are sellers
            SellerProfile.objects.create(user=instance)
