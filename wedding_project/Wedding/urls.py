# accounts/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from Wedding.views import photography, catering, decorations, test_view, venue_view, venue_detail, save_pricing, calculate_price, request_pricing, success_page, send_request, login_success, add_venue, booking_requests, edit_seller_profile


urlpatterns = [
    path('', views.index, name='index'),
    path('subscribe/', views.newsletter_signup, name='newsletter_signup'),
    path('venues/', venue_view, name='venue'),
    path('venues/<int:venue_id>/', venue_detail, name='venue_detail'),
    path('book/venue/<int:venue_id>/', views.book_venue, name='book_venue'),
    path("save-pricing/", save_pricing, name="save_pricing"),
    path("calculate-price/", calculate_price, name="calculate_price"),
    path("success/", success_page, name="success_page"),
    path("request-pricing/", request_pricing, name="request_pricing"),
    path("send-request/", send_request, name="send_request"),
    path('<str:venue_type>/', views.venue_type, name='venue_type'),
    path('services/photography/', photography, name='photography'),


    path('services/catering/', views.catering, name='catering'),
    path('catering/<int:id>/', views.catering_detail, name='catering_detail'),
    path('services/catering/<int:id>/calculate_price/', views.calculate_price, name='calculate_price'),



    path('services/decorations/', views.decorations, name='decorations'),
    #path('venues/<int:venue_id>/', views.venue_detail, name='venue_detail'),
    path('test/', test_view, name='test_view'),
    path('dashboard/contact-us/', views.contact_us, name='contact_us'),

    

    
    # Actor Pages
    path('actor/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/guests/', views.guest_list, name='guest_list'),
    path('dashboard/Addguests/', views.add_guest, name='add_guest'),
    path('dashboard/guests/edit/<int:guest_id>/', views.edit_guest, name='edit_guest'),
    path('dashboard/guests/delete/<int:guest_id>/', views.delete_guest, name='delete_guest'),
    #path('guestconfirmation/', views.guest_confirmation, name='guest_confiramtion'),
    #path('dashboard/send-invitation/', views.send_invitation, name='send_invitation'),
    path('dashboard/guests/send_invitation/<int:guest_id>/', views.send_invitation, name='send_invitation'),
    path('dashboard/generate-invitation/', views.generate_invitation_link, name='generate_invitation_link'),
    path('dashboard/guests/rsvp/<int:guest_id>/', views.rsvp_response, name='rsvp_response'),
    path('dashboard/seating/', views.seating_chart, name='seating_chart'),
    path('dashboard/dietary/', views.dietary_preferences, name='dietary_preferences'),
    path('dashboard/check-in/', views.guest_check_in, name='guest_check_in'),

    path('dashboard/create_event/', views.create_event, name='create_event'),
    path('dashboard/event/<str:unique_token>/', views.event_detail, name='event_detail'),
    path('dashboard/events/', views.event_list, name='event_list'),
    path('dashboard/event/<int:pk>/edit/', views.edit_event, name='edit_event'),
    path('dashboard/event/<int:pk>/delete/', views.delete_event, name='delete_event'),
    #path('event/<int:event_id>/guests/', views.guest_list, name='guest_list'),
    #path('send_invitation/<int:guest_id>/', views.send_invitation, name='send_invitation'),
    #path('rsvp/<int:guest_id>/<str:response>/', views.rsvp_response, name='rsvp_response'),




    path('actor/admin/', views.admin_page, name='admin_page'),
    path('actor/guest/', views.guest_page, name='guest_page'),
    path('actor/seller/', views.sellerdashboard, name='sellerdashboard'),
    path('update-pricing-request-status/<int:request_id>/', views.update_pricing_request_status, name='update_pricing_request_status'),


    path('login_success/', login_success, name='login_success'),
    path('dashboard/edit_seller_profile/', edit_seller_profile, name='edit_seller_profile'),
    path('actor/seller/manage_listings/', views.manage_listings, name='manage_listings'), 
    path('actor/seller/booking_requests/', views.booking_requests, name='booking_requests'),  
    path('actor/seller/reviews/', views.seller_reviews, name='seller_reviews'), 
    path('actor/seller/earnings/', views.earnings, name='earnings'), 
    path('actor/seller/add_venue/', views.add_venue, name='add_venue'), 
    path('actor/seller/edit_venue/<int:venue_id>/', views.edit_venue, name='edit_venue'),
    path('actor/seller/delete-venue/<int:venue_id>/', views.delete_venue, name='delete_venue'),
    path('dashboard/accept_booking/<int:venue_id>/', views.accept_booking, name='accept_booking'),
    path('dashboard/reject_booking/<int:venue_id>/', views.reject_booking, name='reject_booking'),
    path('dashboard/withdraw_funds/<int:venue_id>/', views.withdraw_funds, name='withdraw_funds'),
    path('dashboard/edit_listing/<int:service_id>/', views.edit_listing, name='edit_listing'),
    path('dashboard/add_listing/', views.add_listing, name='add_listing'),
    path('dashboard/delete_listing/<int:service_id>/', views.delete_listing, name='delete_listing'),
    path('venues/filter/', views.filter_venues, name='filter_venues'),


   
    
]
