from django.contrib import admin

# Register your models here.

from .models import Venue, ServiceListing

admin.site.register(Venue)
admin.site.register(ServiceListing)