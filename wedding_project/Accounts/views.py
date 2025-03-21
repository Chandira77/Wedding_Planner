
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile
from Wedding.models import SellerProfile, UserProfile
from django.contrib.auth.decorators import login_required
from Accounts.forms import SignupForm, LoginForm
from Wedding.forms import UserProfileForm, SellerProfileForm
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
            
            try:
                profile = Profile.objects.get(user=user)  # Get user role
            except ObjectDoesNotExist:
                messages.error(request, "Profile not found. Please contact support.")
                return redirect('login')  # Get user role

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
            login(request, user)  # Automatically log in the user after registration
            
            # ✅ Create the appropriate profile
            if role == "seller":
                if not business_category:
                    messages.error(request, "Business category is required for sellers.")
                    return redirect("register")
                SellerProfile.objects.create(user=user, business_category=business_category)
                messages.success(request, "Seller account created successfully!")
                return redirect("seller_dashboard")

            elif role == "user":
                UserProfile.objects.create(user=user)
                messages.success(request, "User account created successfully!")
                return redirect("user_dashboard")

            else:
                messages.success(request, "Account created! Please log in.")
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


# @login_required
# def profile_view(request):
#     seller_profile = get_object_or_404(SellerProfile, user=request.user)  # Fetch current seller's profile
#     return render(request, "Authentication/profile.html", {"seller_profile": seller_profile})

@login_required
def profile_view(request):
    if SellerProfile.objects.filter(user=request.user).exists():
        seller_profile = get_object_or_404(SellerProfile, user=request.user)
        return render(request, "Authentication/profile.html", {"seller_profile": seller_profile})

    elif UserProfile.objects.filter(user=request.user).exists():
        user_profile = get_object_or_404(UserProfile, user=request.user)
        return render(request, "Authentication/profile.html", {"user_profile": user_profile})

    else:
        return redirect("index")
    


@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect("profile")  # Redirect to profile after saving
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, "Authentication/edit_profile.html", {"form": form})