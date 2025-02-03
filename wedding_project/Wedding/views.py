from django.shortcuts import render

# Create your views here.
# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required


# wedding/views.py
from django.shortcuts import render, get_object_or_404
from django import forms
from .models import Venue 
from .forms import VenueSearchForm  

def index(request):
    return render(request, 'Wedding/index.html')

class ExampleForm(forms.Form):
    example_input = forms.CharField(label='Example Input', max_length=100)

def test_view(request):
    form = ExampleForm()
    return render(request, 'Wedding/test.html', {'form': form})

def venue_search(request):
    form = VenueSearchForm(request.GET or None)
    venues = Venue.objects.all()

    if form.is_valid():
        venue_type = form.cleaned_data.get('venue_type')
        city = form.cleaned_data.get('city')
        include_nearby = form.cleaned_data.get('include_nearby')
        guest_number = form.cleaned_data.get('guest_number')
        available_date = form.cleaned_data.get('available_date')

        if venue_type:
            venues = venues.filter(venue_type=venue_type)
        
        if city:
            venues = venues.filter(city__icontains=city)
            if include_nearby:
                pass

        if guest_number:
            if '-' in guest_number:
                min_guest, max_guest = guest_number.split('-')
                venues = venues.filter(capacity_min__lte=int(min_guest), capacity_max__gte=int(max_guest))
            else:
                min_guest = guest_number.replace('+', '')
                venues = venues.filter(capacity_max__gte=int(min_guest))

        if available_date:
            venues = venues.filter(available_dates__date=available_date)

    context = {
        'form': form,
        'venues': venues,
    }
    return render(request, 'Wedding/venue_search.html', context)

def venue_type(request, venue_type):
    # Corrected filter field from 'type' to 'venue_type'
    venues = Venue.objects.filter(venue_type__iexact=venue_type)
    
    context = {
        'venues': venues,
        'venue_type': venue_type.capitalize(),
    }
    return render(request, 'Wedding/venue_type.html', context)

def venue_detail(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    return render(request, 'Wedding/venue_detail.html', {'venue': venue})

def photography(request):
    return render(request, 'Wedding/photography.html')

def catering(request):
    return render(request, 'Wedding/catering.html')

def decorations(request):
    return render(request, 'Wedding/decorations.html')

def contact(request):
    return render(request, 'Wedding/contact.html')

# Actor Pages
def user_page(request):
    return render(request, 'Wedding/user.html')

def admin_page(request):
    return render(request, 'Wedding/admin.html')

def guest_page(request):
    return render(request, 'Wedding/guest.html')

def seller_page(request):
    return render(request, 'Wedding/seller.html')







