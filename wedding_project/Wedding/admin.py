from django.contrib import admin
from .models import Venue, ServiceListing, SellerProfile, UserProfile, Booking, PricingRequest

# Custom Admin for User Management
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'address')
    search_fields = ('user__username', 'full_name', 'phone')
    list_filter = ('user__is_staff', 'user__is_active')

# Custom Admin for Seller Management
@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'phone', 'location', 'average_rating', 'is_seller')
    search_fields = ('business_name', 'user__username', 'phone')
    list_filter = ('is_seller', 'average_rating')

# Custom Admin for Venue Management
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'city', 'price', 'capacity', 'status')
    search_fields = ('name', 'city', 'seller__username')
    list_filter = ('status', 'category', 'venue_type')

# Custom Admin for Service Listings
@admin.register(ServiceListing)
class ServiceListingAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'service_type', 'city', 'status', 'base_price')
    search_fields = ('name', 'seller__username', 'city')
    list_filter = ('service_type', 'status')

# Custom Admin for Bookings
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'venue', 'booking_date', 'status')
    search_fields = ('user__username', 'venue__name')
    list_filter = ('status',)

# Custom Admin for Pricing Requests
@admin.register(PricingRequest)
class PricingRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_name', 'seller_email', 'event_date', 'status')
    search_fields = ('user__username', 'service_name', 'seller_email')
    list_filter = ('status', 'event_date')
