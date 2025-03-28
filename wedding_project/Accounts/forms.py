from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Username is required.'}
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Email is required.', 'invalid': 'Enter a valid email address with @.'}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Password is required.'}
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please confirm your password.'}
    )
    role = forms.ChoiceField(
        choices=[('user', 'User'), ('seller', 'Seller'), ('admin', 'Admin'), ('guest', 'Guest')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    business_category = forms.ChoiceField(
        choices=[
            ('decoration', 'Decoration'),
            ('catering', 'Catering'),
            ('photography', 'Photography'),
            ('videography', 'Videography'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username.isdigit():  # Check if username is only numbers
            raise ValidationError("Username cannot contain only numbers.")
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):  # Only allow alphanumeric and _.- 
            raise ValidationError("Username can only contain letters, numbers, dots, underscores, and hyphens.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")
        if not any(char.isalpha() for char in password):
            raise ValidationError("Password must contain at least one letter.")
        if not any(char in "!@#$%^&*()_+-=" for char in password):
            raise ValidationError("Password must contain at least one special character (!@#$%^&*()_+-=).")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        role = cleaned_data.get("role")
        business_category = cleaned_data.get("business_category")

        if password != confirm_password:
            raise ValidationError("Passwords do not match.")

        if role == 'seller' and not business_category:
            raise ValidationError("Business category is required for sellers.")

        return cleaned_data