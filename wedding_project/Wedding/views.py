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
from .forms import VenueForm
from django.shortcuts import render, get_object_or_404
from django import forms
from .models import Venue 

def index(request):
    venues = Venue.objects.all() 
    return render(request, 'Wedding/index.html', {'venues': venues})

class ExampleForm(forms.Form):
    example_input = forms.CharField(label='Example Input', max_length=100)

def test_view(request):
    form = ExampleForm()
    return render(request, 'Wedding/test.html', {'form': form})

def venue(request):
    form = VenueForm(request.GET or None)
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
    return render(request, 'Wedding/venue.html', context)

@login_required(login_url='/login/')  # Booking requires login
def book_venue(request, venue_id):
    venue = Venue.objects.get(id=venue_id)
    return render(request, 'Wedding/booking.html', {'venue': venue})

def venue_type(request, venue_type):
    return render(request, 'Wedding/venue_type.html', {'venue_type': venue_type})







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


@login_required(login_url='/login/')  # Seller must be logged in
def seller_page(request):
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.seller = request.user  # Set seller to the logged-in user
            venue.save()
            return redirect('Wedding/seller.html')
    else:
        form = VenueForm()

    venues = Venue.objects.filter(seller=request.user)  # Show only seller's venues
    return render(request, 'Wedding/seller.html', {'form': form, 'venues': venues})





