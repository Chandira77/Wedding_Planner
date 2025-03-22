from django import forms
import json
from .models import Venue, ServiceListing, PricingRequest, SellerProfile, UserProfile, Guest, RSVP, Event, NewsletterSubscriber

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
            'amenities': forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter amenities (comma-separated)"}),
            'availability': forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            'base_price': forms.NumberInput(attrs={"class": "form-control", "placeholder": "Base Price"}),
            'extra_guest_price': forms.NumberInput(attrs={"class": "form-control", "placeholder": "Extra Guest Price"}),
            'amenities_price': forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "JSON format"}),
            'image': forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_amenities(self):
        amenities = self.cleaned_data.get('amenities')

        if isinstance(amenities, str):
            # If amenities are in a comma-separated string, split and convert to a list
            amenities_list = [item.strip() for item in amenities.split(',') if item.strip()]
            return amenities_list
        return amenities  # In case it's already a list (from JSON or previous entry)







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
            'service_name', 'first_name', 'last_name',
            'email', 'phone', 'event_date', 'message'
        ]
        widgets = {
            'service_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "Service Name"}),
            'first_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
            'last_name': forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
            'email': forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your Email"}),
            'phone': forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
            'message': forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Your message..."}),
        }

    def save(self, commit=True, user=None, seller_email=None):
        pricing_request = super().save(commit=False)
        if user:
            pricing_request.user = user  # Assign logged-in user
        if seller_email:
            pricing_request.seller_email = seller_email  # Assign seller's email
        if commit:
            pricing_request.save()
        return pricing_request




class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone', 'address', 'profile_picture']



# class EventForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         fields = ['name', 'date', 'venue']

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['event', 'name', 'email', 'phone', 'category', 'assigned_side', 'is_invited']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-control'}),  # Event selection dropdown
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'assigned_side': forms.Select(attrs={'class': 'form-control'}),
            'is_invited': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }




class RSVPForm(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ['event', 'guest', 'response', 'message']
        widgets = {
            'event': forms.Select(attrs={'class': 'form-control'}),  # Event selection dropdown
            'guest': forms.Select(attrs={'class': 'form-control'}),  # Guest selection dropdown
            'response': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PublicRSVPForm(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ['response', 'message']
        widgets = {
            'response': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event', None)
        guest = kwargs.pop('guest', None)
        super().__init__(*args, **kwargs)
        
        if event:
            self.fields['event'] = forms.ModelChoiceField(
                queryset=Event.objects.filter(id=event.id),
                initial=event,
                widget=forms.HiddenInput()
            )
        if guest:
            self.fields['guest'] = forms.ModelChoiceField(
                queryset=Guest.objects.filter(id=guest.id),
                initial=guest,
                widget=forms.HiddenInput()
            )







class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']