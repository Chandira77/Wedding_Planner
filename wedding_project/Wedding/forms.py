# accounts/forms.py

from django import forms
from django.contrib.auth.forms import  AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class VenueSearchForm(forms.Form):
    VENUE_TYPES = [
        ('', 'All Types'),
        ('Temple', 'Temple'),
        ('Hotel', 'Hotel'),
        ('Banquet', 'Banquet'),
        ('Church', 'Church'),
    ]

    venue_type = forms.ChoiceField(choices=VENUE_TYPES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}))
    include_nearby = forms.BooleanField(required=False, label='Include nearby results')
    guest_number = forms.ChoiceField(choices=[
        ('100-200', '100-200'),
        ('200-300', '200-300'),
        ('300-400', '300-400'),
        ('400+', '400+'),
    ], required=False, widget=forms.RadioSelect())
    available_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))


#loginforms
# forms.py



