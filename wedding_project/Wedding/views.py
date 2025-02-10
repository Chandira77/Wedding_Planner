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
from .models import Venue,  Booking, Review, SellerEarnings, PricingRequest
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    venues = Venue.objects.all() 
    return render(request, 'Wedding/index.html', {'venues': venues})

class ExampleForm(forms.Form):
    example_input = forms.CharField(label='Example Input', max_length=100)

def test_view(request):
    form = ExampleForm()
    return render(request, 'Wedding/test.html', {'form': form})



def venue_view(request):
    form = VenueForm(request.GET or None)
    venues = Venue.objects.all()

    # 🔹 **Filtering Logic**
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
                pass  # TODO: Implement nearby search logic

        if guest_number:
            if '-' in guest_number:
                min_guest, max_guest = guest_number.split('-')
                venues = venues.filter(capacity_min__lte=int(min_guest), capacity_max__gte=int(max_guest))
            else:
                min_guest = guest_number.replace('+', '')
                venues = venues.filter(capacity_max__gte=int(min_guest))

        if available_date:
            venues = venues.filter(available_dates__date=available_date)

    # 📌 **Extra Filters from AJAX Request**
    settings = request.GET.getlist('settings')
    amenities = request.GET.getlist('amenities')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort_by', '')

    # 🔹 **Apply Additional Filters**
    if settings:
        venues = venues.filter(settings__in=settings)

    if amenities:
        venues = venues.filter(amenities__name__in=amenities)  # ManyToManyField filter

    if min_price:
        venues = venues.filter(price__gte=min_price)

    if max_price:
        venues = venues.filter(price__lte=max_price)

    # 🔹 **Sorting**
    if sort_by == 'price_low_to_high':
        venues = venues.order_by('price')
    elif sort_by == 'price_high_to_low':
        venues = venues.order_by('-price')
    elif sort_by == 'rating':
        venues = venues.order_by('-rating')
    elif sort_by == 'name':
        venues = venues.order_by('name')

    # 🔹 **Pagination**
    paginator = Paginator(venues, 6)  # Show 6 venues per page
    page_number = request.GET.get('page')
    venues_page = paginator.get_page(page_number)

    # 🔹 **AJAX Response for Dynamic Filtering**
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        venue_data = [
            {
                "id": venue.id,
                "name": venue.name,
                "photo": venue.photo.url if venue.photo else "/static/default.jpg",
                "about": venue.about,
                "amenities": list(venue.amenities.values_list('name', flat=True)),
                "price": venue.price,
                "rating": venue.rating,
                "location": venue.city
            }
            for venue in venues_page
        ]
        return JsonResponse({"venues": venue_data})

    # 🔹 **Render HTML Template**
    context = {
        'form': form,
        'venues': venues_page,
    }
    return render(request, 'Wedding/venue.html', context)


def venue_detail(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    return render(request, 'Wedding/venue_detail.html', {'venue': venue})


@login_required(login_url='/login/')  # Booking requires login
def book_venue(request, venue_id):
    venue = Venue.objects.get(id=venue_id)
    return render(request, 'Wedding/booking.html', {'venue': venue})

def venue_type(request, venue_type):
    return render(request, 'Wedding/venue_type.html', {'venue_type': venue_type})


@csrf_exempt
def request_pricing(request):
    if request.method == "POST":
        venue_id = request.POST.get("venue_id")
        venue_name = request.POST.get("venue_name")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        event_date = request.POST.get("event_date")
        message = request.POST.get("message")

        # Save request to database (optional)
        PricingRequest.objects.create(
            venue_id=venue_id,
            venue_name=venue_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            event_date=event_date,
            message=message
        )

        # Send email to seller (optional)
        send_mail(
            f"New Pricing Request for {venue_name}",
            f"Name: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nEvent Date: {event_date}\nMessage: {message}",
            "admin@yourwebsite.com",
            ["seller@example.com"],
        )

        return JsonResponse({"message": "Your request has been sent successfully!"})

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def send_request(request):
    if request.method == "POST":
        venue_id = request.POST.get("venue_id")
        venue_name = request.POST.get("venue_name")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        event_date = request.POST.get("event_date")
        message = request.POST.get("message")

        # Example: Send Email (modify as needed)
        send_mail(
            subject=f"New Pricing Request for {venue_name}",
            message=f"User {first_name} {last_name} ({email}, {phone}) has requested pricing for {venue_name} on {event_date}.\n\nMessage:\n{message}",
            from_email="noreply@yourdomain.com",
            recipient_list=["seller@example.com"],  # Replace with seller's email
        )

        return JsonResponse({"success": True})
    
    return JsonResponse({"success": False})



def seller_page(request):
    return render(request, 'Wedding/seller_page.html')



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
    venue_type = request.GET.get('venue_type', '')
    city = request.GET.get('city', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    venues = Venue.objects.all()

    if venue_type:
        venues = venues.filter(type=venue_type)
    if city:
        venues = venues.filter(city__icontains=city)
    if min_price and max_price:
        venues = venues.filter(price__gte=min_price, price__lte=max_price)

    venue_list = list(venues.values("id", "name", "location", "price", "photo"))

    return JsonResponse({"venues": venue_view})

def delete_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    venue.delete()  # Delete the venue from the database
    return redirect('manage_listings')


@csrf_exempt
def save_pricing(request):
    if request.method == "POST":
        data = request.POST
        base_price = int(data.get("base_price", 0))
        extra_guest_price = int(data.get("extra_guest_price", 0))
        
        amenities_price = {}
        for key in request.POST.getlist("amenities"):
            amenities_price[key] = int(request.POST.get(f"price_{key}", 0))

        venue = Venue.objects.filter(seller=request.user).first()  # Seller ko venue select garne
        if not venue:
            return JsonResponse({"error": "No venue found!"}, status=400)

        venue.base_price = base_price
        venue.extra_guest_price = extra_guest_price
        venue.amenities_price = amenities_price
        venue.save()

        return JsonResponse({"status": "success"})
    

def calculate_price(request):
    if request.method == "POST":
        data = json.loads(request.body)
        guest_count = int(data.get("guest_count", 0))
        selected_amenities = data.get("amenities", [])

        venue = Venue.objects.first()
        total_price = venue.base_price + (guest_count * venue.extra_guest_price)

        for amenity in selected_amenities:
            if amenity in venue.amenities_price:
                total_price += venue.amenities_price[amenity]

        return JsonResponse({"total_price": total_price})


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







