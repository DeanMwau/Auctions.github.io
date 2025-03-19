from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count
from decimal import Decimal
from django.contrib import messages
from django.db.models import Q
from .models import UserProfile 
from .forms import UserProfileForm, ChangeEmailForm, ListingForm
from django.core.exceptions import ValidationError

from .models import User, Listings, Bids, Watchlists, Comments


def welcome(request):
    listings = Listings.objects.filter(status='active')
    most_bids_listings = Listings.objects.filter(status='active').annotate(bid_count=Count('bids')).filter(bid_count__gt=0).order_by('-bid_count')[:1] # Active listings with bids


    return render(request, "auctions/welcome.html", {
        "listings": listings,
        "most_bids_listings": most_bids_listings,
    })


def index(request):
    listings = Listings.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def closed_listings(request):
    listings = Listings.objects.all()
    closed_listings_found = any(listing.status == "closed" for listing in listings)
    return render(request, "auctions/closed_listings.html", {
        "listings": listings,
        "closed_listings_found": closed_listings_found
    })  

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return redirect("login")
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        location = request.POST.get("location")

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return redirect("register")
        
        if not username:
            messages.error(request, "You must provide a unique username.")
            return redirect("register")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            # Create UserProfile and save location
            UserProfile.objects.create(user=user, location=location)

            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        except IntegrityError as e:
            print(f"IntegrityError during registration: {e}") #print the error.
            messages.error(request, "An unexpected error occurred.")
            return redirect("register")        
        
    else:
        return render(request, "auctions/register.html")
    

@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST.get("title")
        starting_price = request.POST.get("starting_price")
        description = request.POST.get("description")
        image_urls = request.POST.get("image_urls")
        status = request.POST.get("status")
        location = request.POST.get("location")
        category = request.POST.get("category")


        if title and starting_price and description and status and location:
            try:
                # Create a listing
                listing = Listings(
                    seller=request.user, # Use request.user for the seller(currently logged in user)
                    title=title,
                    starting_price=starting_price,
                    current_price=starting_price, #current price should start as starting price or starting bid
                    description=description,
                    image_urls=image_urls,
                    status=status,
                    location=location,
                    category=category,
                )

                listing.full_clean() #Trigger model validation
                listing.save()

                messages.success(request, f"{listing.title} has been listed. Visit your account page to view.")
                return redirect("index")
            
            except ValidationError as e:
                if isinstance(e.messages, list):
                    for msg in e.messages:
                        messages.error(request, msg) # Store each message using Django's messages framework
                else:
                    messages.error(request, str(e))  # Store a single error message if not a list

                return redirect("create")
            
            except IntegrityError:
                messages.error(request, "Listing not listed.")
                return redirect("create")
        else:
            messages.error(request, "All fields are required.")
            return redirect("create")

    else:
        return render(request, "auctions/create_listing.html", {
            'STATUS_CHOICES': Listings.STATUS_CHOICES 
        })

@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)

    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"{listing.title} successfully edited.")
                return redirect('listing', listing_id=listing.id) # redirect to the updated listing detail page
            except IntegrityError as e:
                
                messages.error(request, "A database error occurred. Please try again.")
                return render(request, 'auctions/edit_listing.html', {
                    "form": form,
                    "listing": listing
                })
        else:
            # Store form errors as messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field == "__all__":
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{field.capitalize()}: {error}")
                    
            form.errors.clear()
            return render(request, 'auctions/edit_listing.html', {
                "form": form,
                'listing': listing
            })
            
    form = ListingForm(instance=listing)
    return render(request, 'auctions/edit_listing.html', {
        'form': form, 
        'listing': listing
    })

@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)
    listing.delete()
    messages.success(request, f"{listing.title} deleted successfully.")
    return redirect('account')


def listing_view(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)
    comments = listing.comments.all()

    in_watchlist = False # Initialize in_watchlist to False

    if request.user.is_authenticated:
        in_watchlist = Watchlists.objects.filter(user=request.user, listing=listing).exists()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "listing_bids": listing.bids.all().order_by('-bid_amount'), # bids is a related name in Bids model. Ordered from highest to lowest
        "in_watchlist": in_watchlist,
        "comments": comments
    })


def watch_list(request):
    if request.user.is_authenticated:
        watchlist_items = Watchlists.objects.filter(user=request.user)
        listings = [item.listing for item in watchlist_items]

        winning_bids = {}
        user_won_listings = {} # Dictionary to store listings the user won

        for listing in listings:
            winning_bid_obj = Bids.objects.filter(auction=listing).order_by('-bid_amount').first()

            if winning_bid_obj:
                winning_bids[listing.id] = winning_bid_obj.bid_amount

                # Check if the user won the listing
                if winning_bid_obj.bidder == request.user and listing.status == "closed":
                    user_won_listings[listing.id] = winning_bid_obj.bid_amount
            else:
                winning_bids[listing.id] = None

        return render(request, "auctions/watch_list.html", {
            "listings": listings,
            "winning_bids": winning_bids,
            "user_won_listings": user_won_listings,
        })
    else:
        return redirect(reverse('login') + f'?next={request.path}')


def categories(request):
    categories = Listings.objects.values_list('category', flat=True).distinct()

    categories = categories.exclude(Q(category="") | Q(category__isnull=True))
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category_listings(request, category_name):
    listings = Listings.objects.filter(category=category_name, status='active')
    return render(request, "auctions/category_listings.html", {
        "listings": listings,
        "category_name": category_name
    })


def closed_listing(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)
    comments = listing.comments.all()
    listing_bids = listing.bids.all().order_by('-bid_amount')
    winning_bid = listing_bids.first()

    context = {
        "listing": listing,
        "listing_bids": listing_bids,
        "winning_bid": winning_bid,
        "comments": comments
    }

    if request.user.is_authenticated:
        user_bid = listing_bids.filter(bidder=request.user).first()  # Get the user's bid
        context['user_bid'] = user_bid  # Pass the user's bid to the template


    return render(request, "auctions/closed_listing.html", context)



def add_watchlist(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)

    # Ensure only logged in users can add a listing to a watchlist
    if not request.user.is_authenticated: 
        return redirect(reverse('login') + f'?next={request.path}')
    
    # Ensure a seller cannot add their listing to a watchlist
    if request.user == listing.seller:
        messages.error(request, "You cannot add your own listing to a watchlist.")       
        return redirect("listing", listing_id=listing.id)

    if request.method == "POST":
        try:
            watchlist_item = Watchlists.objects.filter(user=request.user, listing=listing).first()
            if not  watchlist_item:
                Watchlists.objects.create(user=request.user, listing=listing)
                messages.success(request,  f"{listing.title} added to your watchlist.")
            else:
                messages.error(request,  f"{listing.title} is already in your watchlist.")
    
        except Exception as e:
            messages.error(request,  f"An error occurred: {e}")
        
        return redirect("listing", listing_id=listing.id)

    else:
        return redirect("listing", listing_id=listing.id)
    

def remove_watchlist(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)

    if not request.user.is_authenticated:
        return redirect(reverse('login') + f'?next={request.path}')

    if request.method == "POST":
        user = request.user
        try:
            Watchlists.objects.filter(user=user, listing=listing).delete()
            messages.success(request,  f"{listing.title} removed from watchlist successfully.")
        except Exception as e:
            messages.error(request,  f"Error removing from watchlist.: {e}")
        
        return redirect("listing", listing_id=listing.id)
            
        
    return redirect("listing", listing_id=listing.id)
        

def place_bid(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)

    if not request.user.is_authenticated:
        return redirect(reverse('login') + f'?next={request.path}')
    
    if request.user == listing.seller:
        messages.error(request,  "You cannot bid on your own listing.")
        return redirect("listing", listing_id=listing.id)
        
    if request.method == "POST":
        bid_amount = request.POST.get("bidamount")

        if bid_amount:
            try:
                bid_amount_decimal = Decimal(bid_amount)
                latest_highest_bid = listing.bids.order_by('-bid_amount').first()
                
                if latest_highest_bid:
                    if bid_amount_decimal <= latest_highest_bid.bid_amount:
                        messages.error(request,  "Bid must be greater than the current highest bid.")
                        return redirect("listing", listing_id=listing.id)

                else:
                    if bid_amount_decimal < listing.starting_price:
                        messages.error(request,  "Bid amount must be at least as large as the starting price or bid.")
                        return redirect("listing", listing_id=listing.id)
                try:
                    # Create the new bid
                    new_bid = Bids(
                        auction=listing,
                        bidder=request.user,
                        bid_amount=bid_amount_decimal
                    )
                    new_bid.save()

                    listing.current_price = bid_amount_decimal
                    listing.save()
                    
                    messages.success(request, "Bid posted successfully!")
                    return redirect("listing", listing_id=listing.id)
            
                except ValidationError as e:
                    messages.error(request, e.message)
                    return redirect("listing", listing_id=listing.id) 

            except (ValueError, TypeError):
                messages.error(request,  "Invalid bid amount.")

    return redirect("listing", listing_id=listing.id)
                


def close_bidding(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)

    if not request.user.is_authenticated:
        return redirect(reverse('login') + f'?next={request.path}')
    
    if request.method == "POST": 
        if request.user == listing.seller and listing.status == "active":
            listing.status = "closed"
            listing.save()

            messages.success(request,  "Bidding closed successfully.")
        else:
            messages.error(request,  "You are not authorized to close this listing.")

    return redirect("listing", listing_id=listing.id)


def add_comment(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)

    if not request.user.is_authenticated:
        return redirect(reverse('login') + f'?next={request.path}')
    
    if listing.status != "active":
        messages.error(request, "Comments are disabled for closed listings.")
        return redirect("listing", listing_id=listing.id)
    
    if request.method == 'POST':
        comment_text = request.POST.get("comment_text", "").strip()

        if  not comment_text:
            messages.error(request, "Comment cannot be empty.")
            return render(request, "auctions/add_comment.html", {
                "listing": listing
            })
        
        Comments.objects.create(
            user=request.user,
            auction=listing,  # Assuming 'auction' is the ForeignKey in your Comments model
            comment=comment_text
        )
        
        messages.success(request,  "Comment added successfully.")
        return redirect("listing", listing_id=listing.id)
    
    return render(request, "auctions/add_comment.html", {
        "listing": listing
    })


def user_listings(request, username):
    user_profile = get_object_or_404(User, username=username)
    listings = Listings.objects.filter(seller=user_profile)
    return render(request, 'auctions/seller.html', {
        'user_profile': user_profile,
        'listings': listings,
    })


@login_required
def account(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login') + f'?next={request.path}')

    user = request.user
    listings = Listings.objects.filter(seller=user)

    return render(request, 'auctions/accounts.html', {
         'user': user,
         'listings': listings,
     })


@login_required
def change_profile(request):
    user = request.user
    user_profile= user.userprofile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            # Update User model if first_name or last_name are changed
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            user_profile = form.save(commit=False)
            user_profile.user = user
            user_profile.save()

            messages.success(request,  "Changes made successfully.")
            return redirect("account")
        
        else:
            messages.error(request,  "Unable to make profile changes.")        
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'auctions/change_details.html', {
            'form': form
        })


@login_required
def change_email(request):
    user = request.user

    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Email changed successfully.")
            return redirect("account")  
        
        else:
            for field, errors in form.errors.items():
                for error in set(errors):  
                    messages.error(request, f"{error}")
            form.errors.clear()
            return render(request, 'auctions/change_details.html', {'form': form}) 

    form = ChangeEmailForm(instance=user)
    return render(request, 'auctions/change_details.html', {'form': form})




    

            








