from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import VenueForm, ServiceListingForm, SellerProfileForm, GuestForm
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Prefetch
from django import forms
from .models import Venue, ServiceListing, SellerProfile, Booking, Review, SellerEarnings, PricingRequest, Guest, Seating, DietaryPreference, CheckIn
import json
from django.urls import reverse
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
        service_name = request.POST.get("service_name")  # Get service name
        seller_email = request.POST.get("seller_email")  # Get seller's email

        new_request = PricingRequest.objects.create(
            service_name=service_name,
            seller_email=seller_email,
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            email=request.POST["email"],
            phone=request.POST["phone"],
            event_date=request.POST["event_date"],
            message=request.POST["message"],
        )

        # Send email to seller
        send_mail(
            subject=f"New Pricing Request for {service_name}",
            message=f"You have received a new pricing request from {new_request.first_name} {new_request.last_name}.\n\n"
                    f"Service: {service_name}\n"
                    f"Customer Email: {new_request.email}\n"
                    f"Phone: {new_request.phone}\n"
                    f"Event Date: {new_request.event_date}\n"
                    f"Message: {new_request.message}\n\n"
                    "Please check your dashboard to respond.",
            from_email="your-email@example.com",
            recipient_list=[seller_email],  # Send to seller
            fail_silently=False,
        )

        return redirect("success_page")  # Update with your actual success page

    return JsonResponse({"error": "Invalid request"}, status=400)


def success_page(request):
    return render(request, "Wedding/success.html")

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





@login_required
def sellerdashboard(request):
    user = request.user  

    # Check if user is a seller
    try:
        seller_profile = SellerProfile.objects.get(user=user)
    except SellerProfile.DoesNotExist:
        return redirect('seller_registration')  # Redirect to registration page

    # Fetch venues and service listings
    venues = Venue.objects.filter(seller=user).prefetch_related('bookings')
    service_listings = ServiceListing.objects.filter(seller=user)

    # Add withdrawal URL for venues
    for venue in venues:
        venue.withdraw_url = reverse('withdraw_funds', args=[venue.id])

    # Dashboard statistics
    total_venue_listings = venues.count()
    total_service_listings = service_listings.count()
    total_listings = total_venue_listings + total_service_listings 

    total_earnings = SellerEarnings.objects.filter(seller=user).aggregate(Sum('total_earnings'))['total_earnings__sum'] or 0

    # Get different booking statuses
    bookings = Booking.objects.filter(venue__in=venues).select_related('venue')
    pending_bookings = bookings.filter(status='Pending').count()
    confirmed_bookings = bookings.filter(status='Confirmed').count()
    completed_bookings = bookings.filter(status='Completed').count()
    canceled_bookings = bookings.filter(status='Canceled').count()

    # Get recent transactions (last 5 withdrawals)
    recent_transactions = SellerEarnings.objects.filter(seller=user).order_by('created_at')  # ✅ Correct field


    context = {
        'seller': seller_profile,
        'total_listings': total_listings,
        'total_venue_listings': total_venue_listings,
        'total_service_listings': total_service_listings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'completed_bookings': completed_bookings,
        'canceled_bookings': canceled_bookings,
        'total_earnings': total_earnings,
        'venues': venues,
        'service_listings': service_listings,
        'bookings': bookings[:5],  # Show only the latest 5 bookings
        'recent_transactions': recent_transactions,  # Add recent earnings transactions
    }

    return render(request, 'dashboard/sellerdashboard.html', context)
@login_required
def login_success(request):
    if request.user.groups.filter(name="Seller").exists():
        return redirect('sellerdashboard')  
    elif request.user.groups.filter(name="Admin").exists():
        return redirect('admin_dashboard')  
    elif request.user.groups.filter(name="Guest").exists(): 
        return redirect('guest_dashboard')
    elif request.user.groups.filter(name="User").exists():
        return redirect('user_dashboard')
    else:
        return redirect('home')
    

@login_required
def edit_seller_profile(request):
     seller = SellerProfile.objects.filter(user=request.user).first()
     if not seller:
        seller = SellerProfile.objects.create(user=request.user)
     if request.method == 'POST':
        form = SellerProfileForm(request.POST, request.FILES, instance=seller)
        if form.is_valid():
            form.save()
            return redirect('sellerdashboard') 
     else:
        form = SellerProfileForm(instance=seller)

     return render(request, 'dashboard/edit_seller_profile.html', {'form': form})


@login_required
def add_listing(request):
    if request.method == "POST":
        form = ServiceListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)

            # Correctly access the SellerProfile
            try:
                seller_profile = SellerProfile.objects.get(user=request.user)  # Fetch the SellerProfile
                listing.seller = request.user  # Assign the User object, since your model expects User
                listing.save()
                messages.success(request, "Listing added successfully!")
                return redirect('sellerdashboard')
            except SellerProfile.DoesNotExist:
                messages.error(request, "Seller profile not found! Please complete your profile first.")
                return redirect('sellerdashboard')

    else:
        form = ServiceListingForm()

    return render(request, 'dashboard/add_listing.html', {'form': form})


@login_required
def edit_listing(request, service_id):  
    listing = get_object_or_404(ServiceListing, id=service_id, seller=request.user)

    if request.method == "POST":
        form = ServiceListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, "Listing updated successfully!")
            return redirect('sellerdashboard')
    else:
        form = ServiceListingForm(instance=listing)

    return render(request, 'dashboard/edit_listing.html', {'form': form})

@login_required
def delete_listing(request, service_id):
    listing = get_object_or_404(ServiceListing, id=service_id, seller=request.user)  # Directly filter by request.user
    if request.method == "POST":
        listing.delete()
        messages.success(request, "Listing deleted successfully!")
        return redirect('sellerdashboard')

    return render(request, 'wedding/delete_listing.html', {'listing': listing})



@login_required
def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, seller=request.user.seller)

    if request.method == "POST":
        booking.status = "Accepted"
        booking.save()
        messages.success(request, "Booking accepted successfully!")
        return redirect('sellerdashboard')

    return render(request, 'accept_booking.html', {'booking': booking})


@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, seller=request.user.seller)

    if request.method == "POST":
        booking.status = "Rejected"
        booking.save()
        messages.warning(request, "Booking rejected.")
        return redirect('sellerdashboard')

    return render(request, 'reject_booking.html', {'booking': booking})


@login_required
def withdraw_funds(request):
    seller = get_object_or_404(SellerProfile, user=request.user)
    earnings = SellerEarnings.objects.filter(seller=seller)
    total_earnings = earnings.aggregate(total=Sum('amount'))['total'] or 0


    if total_earnings > 0:
        earnings.delete()
        messages.success(request, "Funds withdrawn successfully!")
    else:
        messages.error(request, "No earnings available for withdrawal.")

    return redirect('sellerdashboard')



@login_required(login_url='/login/')
def earnings(request):
    earnings = SellerEarnings.objects.get_or_create(seller=request.user)[0]
    return render(request, 'Wedding/earnings.html', {'earnings': earnings})

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
        service_id = data.get("service_id")  # Service ID from request
        service_type = data.get("service_type")  # Service type (venue/catering/etc.)

        # Determine if it's a venue or another service
        if service_type == "venue":
            service = get_object_or_404(Venue, id=service_id)
        else:
            service = get_object_or_404(ServiceListing, id=service_id)

        # Calculate total price
        total_price = service.base_price + (guest_count * service.extra_guest_price)

        for amenity in selected_amenities:
            if amenity in service.amenities_price:
                total_price += service.amenities_price[amenity]

        return JsonResponse({"total_price": total_price})

def photography(request):
    return render(request, 'Wedding/photography.html')

def catering(request):
    caterings = ServiceListing.objects.filter(service_type="Catering", status="Active") 
    return render(request, 'Wedding/catering.html', {'caterings': caterings})


def catering_detail(request, id):
    service = get_object_or_404(ServiceListing, id=id)
    return render(request, 'Wedding/catering_details.html', {'service': service})


def calculate_price(request, id):
    """AJAX request handler for price calculation."""
    if request.method == "POST":
        service = get_object_or_404(ServiceListing, id=id)
        guests = int(request.POST.get('guests', 0))
        selected_amenities = request.POST.getlist('amenities')

        total_price = service.calculate_price(guests, selected_amenities)
        return JsonResponse({'total_price': total_price})



def decorations(request):
    return render(request, 'Wedding/decorations.html')

def contact(request):
    return render(request, 'Wedding/contact.html')

# Actor Pages


@login_required
def user_dashboard(request):
    return render(request, 'dashboard/user_dashboard.html')





@login_required
def guest_list(request):
    guest_objects = Guest.objects.all()  # Fetch all guests
    paginator = Paginator(guest_objects, 5)  # Show 5 guests per page
    page_number = request.GET.get('page')
    guests = paginator.get_page(page_number)
    
    return render(request, 'dashboard/guest_list.html', {'guests': guests})



# Add a new guest
def add_guest(request):
    if request.method == "POST":
        form = GuestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('guest_list')
    else:
        form = GuestForm()
    return render(request, 'add_guest.html', {'form': form})

# Edit guest details
def edit_guest(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    if request.method == "POST":
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            form.save()
            return redirect('guest_list')
    else:
        form = GuestForm(instance=guest)
    return render(request, 'edit_guest.html', {'form': form, 'guest': guest})

# Delete guest
def delete_guest(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    if request.method == "POST":
        guest.delete()
        return redirect('guest_list')
    return render(request, 'guest_confirm_delete.html', {'guest': guest})

# 🎯 SEND INVITATION EMAIL
@login_required
def send_rsvp(request):
    guests = Guest.objects.all()
    return render(request, 'dashboard/send_rsvp.html', {'guests': guests})



@login_required
def seating_chart(request):
    seatings = Seating.objects.all()
    return render(request, 'dashboard/seating_chart.html', {'seatings': seatings})


@login_required
def dietary_preferences(request):
    preferences = DietaryPreference.objects.all()
    return render(request, 'dashboard/dietary_preferences.html', {'preferences': preferences})


@login_required
def guest_check_in(request):
    checked_in_guests = CheckIn.objects.all()
    return render(request, 'dashboard/guest_check_in.html', {'checked_in_guests': checked_in_guests})



# 🎯 RSVP RESPONSE (Accept or Decline)
def rsvp_response(request, guest_id, response):
    guest = get_object_or_404(Guest, id=guest_id)
    if response in ['Accepted', 'Declined']:
        guest.rsvp_status = response
        guest.save()
    return render(request, 'dashboard/rsvp_response.html', {'guest': guest})

def admin_page(request):
    return render(request, 'Wedding/admin.html')

def guest_page(request):
    return render(request, 'Wedding/guest.html')







