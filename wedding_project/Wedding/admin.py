from django.contrib import admin

# Register your models here.

from .models import Venue, Amenity

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue_type', 'city', 'price')
    list_filter = ('venue_type', 'city')
    search_fields = ('name', 'address')

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
