from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
from Accounts.views import logout_view, profile_view, edit_profile
urlpatterns =[
    path('login/', views.login_view, name='login'),
    #path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path('register/', views.register_view, name='register'),
]