from django import forms
import json
from .models import Venue, ServiceListing, PricingRequest, SellerProfile

class VenueForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=[('Available', 'Available'), ('Unavailable', 'Unavailable')],
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Venue
        fields = [
            'name', 'description', 'city', 'price', 'capacity', 
            'amenities', 'availability', 'image', 'status',
            'base_price', 'extra_guest_price', 'amenities_price'
        ]
        widgets = {
            'name': forms.TextInput(attrs={"class": "form-control", "placeholder": "Venue Name"}),
            'description': forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Venue Description"}),
            'city': forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            'price': forms.NumberInput(attrs={"class": "form-control", "placeholder": "Price"}),
            'capacity': forms.NumberInput(attrs={"class": "form-control", "placeholder": "Capacity"}),
            'amenities': forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Comma-separated amenities"}),
            'availability': forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            'base_price': forms.NumberInput(attrs={"class": "form-control", "placeholder": "Base Price"}),
            'extra_guest_price': forms.NumberInput(attrs={"class": "form-control", "placeholder": "Extra Guest Price"}),
            'amenities_price': forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "JSON format"}),
            'image': forms.ClearableFileInput(attrs={"class": "form-control"}),
        }




class ServiceListingForm(forms.ModelForm):
    # Amenities pricing input as JSON string
    amenities_price = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter amenities price as JSON, e.g., {"Wifi": 10, "Decoration": 50}'}),
        required=False
    )

    class Meta:
        model = ServiceListing
        fields = ['service_type', 'base_price', 'extra_guest_price', 'amenities_price', 
                  'availability', 'category', 'city', 'status', 'images']
        widgets = {
            'availability': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amenities_price(self):
        """Validate amenities_price field to ensure proper JSON format."""
        data = self.cleaned_data.get('amenities_price', '{}')
        try:
            return json.loads(data) if data else {}
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON format for amenities price. Example: {'Wifi': 10, 'Decoration': 50}")

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['business_name', 'phone', 'profile_image', 'location', 'description', 'services', 'website']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter business name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write about your business'}),
            'services': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List your services'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter website URL (optional)'}),
        }


class PricingRequestForm(forms.ModelForm):
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = PricingRequest
        fields = [
            'service_name', 'seller_email', 'first_name', 'last_name',
            'email', 'phone', 'event_date', 'message'
        ]
        widgets = {
            'service_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "Service Name"}),
            'seller_email': forms.EmailInput(attrs={"class": "form-control", "placeholder": "Seller Email"}),
            'first_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
            'last_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
            'email': forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your Email"}),
            'phone': forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
            'message': forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Your message..."}),
        }