
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm
from django.contrib.auth import authenticate, login, logout

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
                return redirect('user_page')
            elif profile.role == 'seller':
                return redirect('seller_page')
            elif profile.role == 'admin':
                return redirect('admin_page')
            elif profile.role == 'guest':
                return redirect('guest_page')
        else:
            messages.error(request, "Invalid credentials")
    
    return render(request, 'Authentication/login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        role = request.POST["role"]  # Get role from form

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Choose another.")
            return redirect("Authentication/register.html")

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use. Use another email.")
            return redirect("Authentication/register.html")

        # Check password confirmation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("Authentication/register.html")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Assign role to profile
        profile = Profile.objects.create(user=user, role=role)
        profile.save()

        messages.success(request, "Registration successful! You can now log in.")
        return redirect("login")

    return render(request, "Authentication/register.html")


def send_welcome_email(user_email):
    subject = "Welcome to Wedding Organizer"
    message = "Thank you for registering on our platform."
    from_email = 'inachand920@gmail.com'  # This should match DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)