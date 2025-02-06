from django import forms

from .models import Venue

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'description', 'city', 'price', 'capacity', 'amenities', 'availability', 'image']
