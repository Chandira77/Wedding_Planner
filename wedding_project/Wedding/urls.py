# accounts/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from Wedding.views import photography, catering, decorations, contact, test_view, venue, venue_detail, save_pricing, calculate_price, request_pricing, send_request, add_venue, booking_requests


urlpatterns = [
    path('', views.index, name='index'),
    #path('services/', ServicesView.as_view(), name='services'),
    path('venues/', venue, name='venue'),
    #path('venues/', venue_list, name='venues_list'),
    path('venues/<int:venue_id>/', venue_detail, name='venue_detail'),
    path('book/venue/<int:venue_id>/', views.book_venue, name='book_venue'),
    path("save-pricing/", save_pricing, name="save_pricing"),
    path("calculate-price/", calculate_price, name="calculate_price"),
    path("request-pricing/", request_pricing, name="request_pricing"),
    path("send-request/", send_request, name="send_request"),
    path('<str:venue_type>/', views.venue_type, name='venue_type'),
    path('services/photography/', photography, name='photography'),
    path('services/catering/', views.catering, name='catering'),
    path('services/decorations/', views.decorations, name='decorations'),
    #path('venues/<int:venue_id>/', views.venue_detail, name='venue_detail'),
    path('test/', test_view, name='test_view'),
    path('contact/', views.contact, name='contact'),
    
    # Actor Pages
    path('actor/user/', views.user_page, name='user_page'),
    path('actor/admin/', views.admin_page, name='admin_page'),
    path('actor/guest/', views.guest_page, name='guest_page'),
    path('actor/seller/', views.seller_page, name='seller_page'),


    path('actor/seller/add_venue/', views.add_venue, name='add_venue'),  # Add venue for sellers
    path('actor/seller/manage_listings/', views.manage_listings, name='manage_listings'),  # Manage venue listings
    path('actor/seller/booking_requests/', views.booking_requests, name='booking_requests'),  # View booking requests (accept/reject)
    path('actor/seller/reviews/', views.seller_reviews, name='seller_reviews'),  # Seller's reviews page
    path('actor/seller/payment_management/', views.payment_management, name='payment_management'),  # Seller's payment and revenue page
    path('actor/seller/edit_venue/<int:venue_id>/', views.edit_venue, name='edit_venue'),
    path('actor/seller/delete-venue/<int:venue_id>/', views.delete_venue, name='delete_venue'),
    path('venues/filter/', views.filter_venues, name='filter_venues'),


   
    
]
