from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class SignupForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
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
        required=False,  # Only required for sellers
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        role = cleaned_data.get("role")
        business_category = cleaned_data.get("business_category")

        # Validate password confirmation
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")

        # Validate business_category only if role is 'seller'
        if role == 'seller' and not business_category:
            raise ValidationError("Business category is required for sellers.")
