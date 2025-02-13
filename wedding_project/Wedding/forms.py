from django import forms

from .models import Venue, PricingRequest, SellerProfile

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





class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['business_name', 'phone', 'profile_image']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter business name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


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