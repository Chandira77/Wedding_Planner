from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import VenueForm
from django.core.paginator import Paginator
from django.db.models import Q
from django import forms
from .models import Venue,  Booking, Review, SellerEarnings
from django.http import JsonResponse

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

    # Filtering Logic
    if form.is_valid():
        venue_type = form.cleaned_data.get('venue_type')
        city = form.cleaned_data.get('city')
        include_nearby = form.cleaned_data.get('include_nearby')
        guest_number = form.cleaned_data.get('guest_number')
        available_date = form.cleaned_data.get('available_date')

        if venue_type:
            venues = venues.filter(venue_type=venue_type)
        
        if city:
            venues = venues.filter(Q(city__icontains=city))
            if include_nearby:
                # Implement nearby search logic here
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

    # Sorting (By Price, Rating, etc.)
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_low_to_high':
        venues = venues.order_by('price')
    elif sort_by == 'price_high_to_low':
        venues = venues.order_by('-price')
    elif sort_by == 'rating':
        venues = venues.order_by('-rating')

    # Pagination
    paginator = Paginator(venues, 6)  # Show 6 venues per page
    page_number = request.GET.get('page')
    venues_page = paginator.get_page(page_number)

    if not venues.exists():
        messages.info(request, "No venues found matching your filters.")

    context = {
        'form': form,
        'venues': venues_page,
    }
    return render(request, 'Wedding/venue.html', context)

def venue_list(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # AJAX request
        venue_type = request.GET.get('venue_type', '')
        city = request.GET.get('city', '')
        guest_numbers = request.GET.get('guest_number', '').split(',')
        settings = request.GET.get('settings', '').split(',')
        amenities = request.GET.get('amenities', '').split(',')

        venues = Venue.objects.all()

        if venue_type and venue_type != "all":
            venues = venues.filter(type=venue_type)
        if city:
            venues = venues.filter(city__icontains=city)
        if guest_numbers:
            venues = venues.filter(guest_capacity__in=guest_numbers)
        if settings:
            venues = venues.filter(settings__in=settings)
        if amenities:
            venues = venues.filter(amenities__contains=amenities)

        venue_data = [
            {
                "name": venue.name,
                "photo": venue.photo.url if venue.photo else "/static/default.jpg",
                "about": venue.about,
                "amenities": venue.amenities
            }
            for venue in venues
        ]
        return JsonResponse({"venues": venue_data})

    venues = Venue.objects.all()
    return render(request, "Wedding/venue.html", {"venues": venues})


@login_required(login_url='/login/')  # Booking requires login
def book_venue(request, venue_id):
    venue = Venue.objects.get(id=venue_id)
    return render(request, 'Wedding/booking.html', {'venue': venue})

def venue_type(request, venue_type):
    return render(request, 'Wedding/venue_type.html', {'venue_type': venue_type})



@login_required(login_url='/login/')
def seller_page(request):
    venues = Venue.objects.filter(seller=request.user)
    bookings = Booking.objects.filter(venue__seller=request.user)
    earnings = SellerEarnings.objects.get_or_create(seller=request.user)[0]
    
    context = {
        'venues': venues,
        'bookings': bookings,
        'earnings': earnings,
    }
    return render(request, 'Wedding/seller.html', context)



@login_required(login_url='/login/')
def add_venue(request):
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.seller = request.user
            venue.save()
            return redirect('manage_listings')
    else:
        form = VenueForm()

    return render(request, 'Wedding/add_venue.html', {'form': form})

@login_required(login_url='/login/')
def manage_venues(request):
    venues = Venue.objects.filter(seller=request.user)
    return render(request, 'Wedding/manage_venues.html', {'venues': venues})

@login_required(login_url='/login/')
def manage_listings(request):
    # Fetch the venues added by the logged-in seller
    venues = Venue.objects.filter(seller=request.user)
    return render(request, 'Wedding/manage_listings.html', {'venues': venues})

@login_required(login_url='/login/')
def booking_requests(request):
    bookings = Booking.objects.filter(venue__seller=request.user)
    return render(request, 'Wedding/booking_requests.html', {'bookings': bookings})

@login_required(login_url='/login/')
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = status
    booking.save()
    return redirect('booking_requests')

def seller_reviews(request):
    reviews = Review.objects.filter(venue__seller=request.user)  # Seller's reviews
    return render(request, 'Wedding/seller_reviews.html', {'reviews': reviews})


@login_required(login_url='/login/')
def earnings(request):
    earnings = SellerEarnings.objects.get_or_create(seller=request.user)[0]
    return render(request, 'Wedding/earnings.html', {'earnings': earnings})

def payment_management(request):
    # Logic for managing payments and revenue
    return render(request, 'Wedding/payment_management.html')

def edit_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    if request.method == "POST":
        form = VenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            return redirect('manage_listings')  # Redirect after successful edit
    else:
        form = VenueForm(instance=venue)
    return render(request, 'Wedding/edit_venue.html', {'form': form, 'venue': venue})


def filter_venues(request):
    if request.method == "GET":
        venue_type = request.GET.get('venue_type', None)
        location = request.GET.get('location', None)
        price_range = request.GET.get('price_range', None)

        venues = Venue.objects.all()  # All venues

        if venue_type:
            venues = venues.filter(type=venue_type)
        if location:
            venues = venues.filter(location__icontains=location)
        if price_range:
            min_price, max_price = map(int, price_range.split('-'))
            venues = venues.filter(price__gte=min_price, price__lte=max_price)

        venue_data = list(venues.values('id', 'name', 'location', 'price'))  # Convert QuerySet to JSON format
        return JsonResponse({'venues': venue_data})


def delete_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    venue.delete()  # Delete the venue from the database
    return redirect('manage_listings')


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







