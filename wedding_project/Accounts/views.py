
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile
from Wedding.models import SellerProfile
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm
from django.contrib.auth import get_user_model, authenticate, login, logout

# wedding/views.py
from django.shortcuts import render, get_object_or_404
from django import forms

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Log the user in
            profile = Profile.objects.get(user=user)  # Get user role

            # Redirect based on role
            if profile.role == 'user':
                return redirect('user_dashboard')
            elif profile.role == 'seller':
                return redirect('sellerdashboard')
            elif profile.role == 'admin':
                return redirect('admin_page')
            elif profile.role == 'guest':
                return redirect('guest_page')
        else:
            messages.error(request, "Invalid credentials")
    
    return render(request, 'Authentication/login.html')


User = get_user_model()  # Get the custom user model if using custom User model

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")  
        business_category = request.POST.get("business_category")  # Get seller's category

        # Validate input
        if not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Choose another.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use. Use another email.")
            return redirect("register")

        # Ensure role is valid
        valid_roles = ["user", "seller", "admin", "guest"]
        if role not in valid_roles:
            messages.error(request, "Invalid role selected.")
            return redirect("register")

        # ✅ Create user and profile
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # ✅ If seller, include business category, otherwise keep it empty
            if role == "seller" and not business_category:
                messages.error(request, "Business category is required for sellers.")
                return redirect("register")

            Profile.objects.create(
                user=user, 
                role=role, 
                business_category=business_category if role == "seller" else None
            )

            messages.success(request, "Registration successful! You can now log in.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect("register")

    return render(request, "Authentication/register.html")


def send_welcome_email(user_email):
    subject = "Welcome to Wedding Organizer"
    message = "Thank you for registering on our platform."
    from_email = 'inachand920@gmail.com'  # This should match DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)


def logout_view(request):
    logout(request)  # Logs out the current user
    return redirect('login')  # Redirects to login page after logout


@login_required
def profile_view(request):
    seller_profile = get_object_or_404(SellerProfile, user=request.user)  # Fetch current seller's profile
    return render(request, "Authentication/profile.html", {"seller_profile": seller_profile})