from django import forms

from .models import Venue, PricingRequest

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'description', 'city', 'price', 'capacity', 'amenities', 'availability', 'image']


class PricingRequestForm(forms.ModelForm):
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = PricingRequest
        fields = ['venue', 'first_name', 'last_name', 'email', 'phone', 'event_date', 'message']
        widgets = {
            'venue': forms.Select(attrs={"class": "form-control"}),
            'first_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
            'last_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
            'email': forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            'phone': forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
            'message': forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Your message..."}),
        }
