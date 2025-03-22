from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import VenueForm, ServiceListingForm, SellerProfileForm, GuestForm, RSVPForm, NewsletterForm
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Prefetch
from django import forms
from .models import Venue, ServiceListing, SellerProfile, Booking, Review, SellerEarnings, PricingRequest, Guest, RSVP, Event, Seating, DietaryPreference, CheckIn
import json, uuid
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    venues = Venue.objects.all() 
    return render(request, 'Wedding/index.html', {'venues': venues})



def newsletter_signup(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for subscribing!")
            return redirect('home')  # Redirect to home page (change as needed)
    else:
        form = NewsletterForm()

    return render(request, 'partials/footer.html', {'form': form})

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


@login_required
@csrf_exempt
def request_pricing(request):
    if request.method == "POST":
        service_name = request.POST.get("service_name")  
        seller_email = request.POST.get("seller_email")  

        # Debugging: Check if the seller email is being received correctly
        print(f"Seller email received: {seller_email}")

        # Find the seller profile using the email (case-insensitive)
        seller = SellerProfile.objects.filter(user__email__iexact=seller_email).first()
        if not seller:
            print(f"Seller with email {seller_email} not found.")
            return JsonResponse({"error": "Seller not found"}, status=400)

        # Ensure the seller is properly linked
        if not seller.user:
            print(f"Seller {seller_email} does not have a valid user account.")
            return JsonResponse({"error": "Seller is not linked to a user"}, status=400)

        # Create Pricing Request entry
        new_request = PricingRequest.objects.create(
            user=request.user,
            seller=seller,  # Ensure the seller is properly linked
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
            message=f"""
            You have received a new pricing request from {new_request.first_name} {new_request.last_name}.

            Service: {service_name}
            Customer Email: {new_request.email}
            Phone: {new_request.phone}
            Event Date: {new_request.event_date}
            Message: {new_request.message}

            Please check your dashboard to respond.
            """,
            from_email=new_request.email,
            recipient_list=[seller_email],
            fail_silently=False,
        )

        messages.success(request, 'Your pricing request has been sent successfully!')

        return redirect("success_page")

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

        # Get seller email from venue model (Assuming Venue model exists)
        try:
            venue = Venue.objects.get(id=venue_id)  
            seller_email = venue.seller.email  # Seller को email निकाल्ने 
        except Venue.DoesNotExist:
            return JsonResponse({"error": "Venue not found"}, status=404)

        # Save to database (so it appears in seller's dashboard)
        new_request = PricingRequest.objects.create(
            user=request.user,  
            service_name=venue_name,
            seller_email=seller_email,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            event_date=event_date,
            message=message,
        )

        # Send email to seller
        send_mail(
            subject=f"New Pricing Request for {venue_name}",
            message=f"""
            You have received a new pricing request from {new_request.first_name} {new_request.last_name}.

            Service: {venue_name}
            Customer Email: {new_request.email}
            Phone: {new_request.phone}
            Event Date: {new_request.event_date}
            Message: {new_request.message}

            Please check your dashboard to respond.
            """,
            from_email=email,
            recipient_list=[seller_email],
            fail_silently=False,
            headers={"Reply-To": email},
        )

        return JsonResponse({"success": True, "message": "Your pricing request has been sent!"})

    return JsonResponse({"error": "Invalid request"}, status=400)






@login_required
def sellerdashboard(request):
    user = request.user  

    # Check if user is a seller
    try:
        seller_profile = SellerProfile.objects.get(user=user)
    except SellerProfile.DoesNotExist:
        return redirect('seller_registration')  # Redirect to registration page

    # Fetch venues and service listings
    venues = Venue.objects.filter(seller=user).prefetch_related('booking_set')  # Updated prefetch for bookings
    service_listings = ServiceListing.objects.filter(seller=user).select_related('category')

    # Add withdrawal URL for venues
    for venue in venues:
        venue.withdraw_url = reverse('withdraw_funds', args=[venue.id])

    # Dashboard statistics
    total_venue_listings = venues.count()
    total_service_listings = service_listings.count()
    total_listings = total_venue_listings + total_service_listings 

    total_earnings = SellerEarnings.objects.filter(seller=user).aggregate(Sum('total_earnings'))['total_earnings__sum'] or 0

    # Get different booking statuses efficiently
    pending_bookings = Booking.objects.filter(venue__in=venues, status='Pending').count()
    confirmed_bookings = Booking.objects.filter(venue__in=venues, status='Confirmed').count()
    completed_bookings = Booking.objects.filter(venue__in=venues, status='Completed').count()
    canceled_bookings = Booking.objects.filter(venue__in=venues, status='Canceled').count()

    # Get recent transactions (last 5 withdrawals)
    recent_transactions = SellerEarnings.objects.filter(seller=user).order_by('-created_at')[:5]  # Get the latest 5

    # Pricing requests for the seller
    pricing_requests = PricingRequest.objects.filter(seller=seller_profile).order_by('-created_at')

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
        'bookings': Booking.objects.filter(venue__in=venues).select_related('venue', 'user').order_by('-booking_date')[:5],  # Latest bookings
        'recent_transactions': recent_transactions,
        'pricing_requests': pricing_requests,
    }

    return render(request, 'dashboard/sellerdashboard.html', context)







@login_required
def update_pricing_request_status(request, request_id):
    if request.method == "POST":
        try:
            pricing_request = PricingRequest.objects.get(id=request_id, seller_email=request.user.email)
            new_status = request.POST.get("status")
            if new_status in ["Pending", "Approved", "Rejected"]:
                pricing_request.status = new_status
                pricing_request.save()
                messages.success(request, f"Pricing request status updated to {new_status}.")
            else:
                messages.error(request, "Invalid status update.")
        except PricingRequest.DoesNotExist:
            messages.error(request, "Request not found.")
    
    return redirect("sellerdashboard")






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
            # Save the form and ensure the image is saved
            form.save()
            return redirect('manage_listings')  # Redirect after successful edit
    else:
        form = VenueForm(instance=venue)  # Pre-populate the form with the existing venue data

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


def contact_us(request):
    return render(request, 'dashboard/contact_us.html')

# Actor Pages


@login_required
def user_dashboard(request):
    user = request.user
    events = Event.objects.filter(created_by=user)  # Fetch events created by logged-in user
    guests = Guest.objects.filter(event__in=events)  # Fetch guests for events
    
    context = {
        'events': events,
        'guests': guests,
    }
    return render(request, 'dashboard/user_dashboard.html', context)





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
    return render(request, 'dashboard/add_guest.html', {'form': form})

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
    return render(request, 'dashboard/edit_guest.html', {'form': form, 'guest': guest})

# Delete guest
def delete_guest(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    if request.method == "POST":
        guest.delete()
        return redirect('guest_list')
    return render(request, 'dashboard/guest_confirm_delete.html', {'guest': guest})

# 🎯 SEND INVITATION EMAIL
@login_required
def send_invitation(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)

    if guest.is_invited:
        messages.warning(request, f"Invitation already sent to {guest.name}.")
    else:

        user = request.user
        from_email = user.email

        # Send email logic
        send_mail(
            subject="Wedding Invitation",
            message=f"Dear {guest.name},\n\nYou are invited to our wedding! Please RSVP using this link: {request.build_absolute_uri(reverse('rsvp_response', args=[guest.id]))}",
            from_email=from_email,
            recipient_list=[guest.email],
            fail_silently=False,
        )

        # Mark invitation as sent
        guest.is_invited = True
        guest.save()

        messages.success(request, f"Invitation sent to {guest.name} successfully!")

    return redirect('guest_list')



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
def rsvp_response(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    event = guest.event  # Assuming Guest model has event field

    # Fetch or create RSVP entry for this guest
    rsvp, created = RSVP.objects.get_or_create(guest=guest, defaults={'event': event})

    if request.method == "POST":
        form = RSVPForm(request.POST, instance=rsvp)  # Pass instance to update existing RSVP
        if form.is_valid():
            form.save()
            messages.success(request, "RSVP response recorded successfully!")
            return redirect('guest_list')  # Redirect to guest list view (update as needed)
    else:
        form = RSVPForm(instance=rsvp)  # Pre-fill form if RSVP exists

    return render(request, 'dashboard/rsvp_response.html', {'form': form, 'guest': guest})


@login_required
def create_event(request):
    if request.method == "POST":
        name = request.POST.get("name")
        date = request.POST.get("date")
        time = request.POST.get("time")
        venue = request.POST.get("venue")
        
        unique_token = uuid.uuid4().hex[:10]  # Random token (10 chars)
        invite_link = f"http://127.0.0.1:8000/invite/{unique_token}"  # Change for deployment
        
        event = Event.objects.create(
            name=name,
            date=date,
            time=time,
            venue=venue,
            created_by=request.user,
            invite_link=invite_link,
            unique_token=unique_token
        )
        return JsonResponse({"success": True, "invite_link": invite_link})
    
    return JsonResponse({"success": False, "message": "Invalid Request"})



# def event_detail(request, pk):
#     event = get_object_or_404(Event, pk=pk, created_by=request.user)
#     return render(request, 'dashboard/event_details.html', {'event': event})



def event_detail(request, unique_token):  # Accept unique_token
    event = get_object_or_404(Event, unique_token=unique_token)  # Retrieve event using unique_token

    return render(request, 'dashboard/event_details.html', {'event': event})

def event_list(request):
    events = Event.objects.filter(created_by=request.user)  # Current user ko events matra dekhaucha
    return render(request, 'dashboard/event_list.html', {'events': events})





def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk, created_by=request.user)

    if request.method == "POST":
        event.name = request.POST['name']
        event.date = request.POST['date']
        event.time = request.POST['time']
        event.venue = request.POST['venue']
        event.save()
        return redirect('event_detail', pk=event.pk)

    return render(request, 'dashboard/edit_event.html', {'event': event})



def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk, created_by=request.user)

    if request.method == "POST":
        event.delete()
        return redirect('user_dashboard')

    return render(request, 'dashboard/delete_event.html', {'event': event})


def event_invite(request, token):
    event = get_object_or_404(Event, unique_token=token)
    return render(request, "event_invite.html", {"event": event})



@login_required
def generate_invitation_link(request):
    try:
        event = Event.objects.filter(created_by=request.user).latest('id')  # Get latest event
        if not event.unique_token:
            event.unique_token = uuid.uuid4().hex[:10]  # Generate unique token only if not set
        
        # Generate a shareable link to the event details page
        event.invite_link = request.build_absolute_uri(reverse('event_detail', args=[event.unique_token]))
        event.save()

        print("Generated Invite Link:", event.invite_link)  # Debugging

        return render(request, 'dashboard/generate_invitation_link.html', {'invite_link': event.invite_link})
    except Event.DoesNotExist:
        return JsonResponse({'error': 'No event found'}, status=400)





def view_invitation(request, invite_token):
    event = get_object_or_404(Event, invite_link__contains=invite_token)
    return render(request, 'dashboard/invitation_page.html', {'event': event})




def admin_page(request):
    return render(request, 'Wedding/admin.html')

def guest_page(request):
    return render(request, 'Wedding/guest.html')







