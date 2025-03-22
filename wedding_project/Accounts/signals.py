from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from  Wedding.models import SellerProfile
from Accounts.models import Profile

@receiver(post_save, sender=User)
def create_seller_profile(sender, instance, created, **kwargs):
    if created:  # Runs only when a new user is created
        if instance.is_staff:  # Assuming staff users are sellers
            SellerProfile.objects.create(user=instance)



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
