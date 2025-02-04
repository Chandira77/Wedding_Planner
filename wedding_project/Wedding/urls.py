# accounts/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from Wedding.views import photography, catering, decorations, contact, test_view, venue


urlpatterns = [
    path('', views.index, name='index'),
    #path('services/', ServicesView.as_view(), name='services'),
    path('venues/', venue, name='venue'),
    path('book/venue/<int:venue_id>/', views.book_venue, name='book_venue'),
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

    # registration templates
    #path('login/', views.login_view, name='login'),
   
    #path('dashboard/', views.account_dashboard, name='account_dashboard'),
]
