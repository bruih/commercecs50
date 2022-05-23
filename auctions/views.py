from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import whenCreatingListingForms
from .models import *




def index(request):
    listings = {
    'listings': Listing.objects.filter(sold=False)
    }
    return render(request, "auctions/index.html", listings)


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

        
@login_required
def listingInfos(request, listingId):
    listing = Listing.objects.get(id=listingId)
    user = request.user
    owner = listing.user
    if owner == user:
        True
    else:
        False
    category = Category.objects.get(category=listing.category)
    comments = Comment.objects.filter(listing=listing.id)
    watching = Watchlist.objects.filter(user = user, listing = listing)
    if watching:
        watching = Watchlist.objects.get(user = user, listing = listing)
    return listing, user, owner, category, comments, watching

@login_required
def listing(request, listingId):
    info = listingInfos(request, listingId)
    listing, user, owner, category = info[0], info[1], info[2], info[3]
    if request.method == "POST":
        comment = request.POST["comment"]
        if comment != "":
            Comment.objects.create(user = user, listing = listing, comment = comment)
    context = {
        "listing": listing,
        "category": category,
        "comments":Comment.objects.filter(listing=listing.id), 
        "watching": Watchlist.objects.filter(user = user, listing = listing).values('watching'), 
        "owner": owner,
    }
    return render(request, "auctions/listings.html", context)

@login_required
def addingWatchlist(request, listingId):
    info = listingInfos(request, listingId)
    listing, user, owner, category, comments = info[0], info[1], info[2], info[3]
    watch = Watchlist.objects.filter(user = user, listing = listing)
    if watch:
        watch = Watchlist.objects.get(user = user, listing = listing)
        watch.watching = True
        watch.save()
    else:
        Watchlist.objects.create(user = user, listing = listing, watching = True)
    context = {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": Watchlist.objects.get(user = user, listing = listing).watching, 
        "owner": owner,
    }
    return render(request, "auctions/listings.html", context)

@login_required
def removingWatchlist(request, listingId):
    info = listingInfos(request, listingId)
    listing, user, owner, category, comments, watch = info[0], info[1], info[2], info[3], 
    watch.watching = False
    watch.save()
    context = {
        "listing": listing,
        "category": category,"comments": comments, 
        "watching": Watchlist.objects.get(user = user, listing = listing).watching, 
        "owner": owner,
    }
    return render(request, "auctions/listings.html", context)

@login_required
def bid(request, listingId):
    info = listingInfos(request, listingId)
    listing, user, owner, category, comments, watch = info[0], info[1], info[2], info[3]
    if request.method == "POST":
        bid = request.POST["bid"]
        listing.price = float(bid)
        listing.save()
        Bid.objects.create(user = user, price = bid, listing = listing)
    context = {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": watch, 
        "owner": owner,
    }
    return render(request, "auctions/listings.html", context)


@login_required
def closingBid(request, listingId):
    info = listingInfos(request, listingId)
    listing, user, category, owner, comments, watch = info[0], info[1], info[2], info[3]
    listing.sold = True
    listing.save()
    winner = Bid.objects.get(price = listing.price, listing = listing).user
    print(user.id, winner.id)
    winning = user.id == winner.id
    thewinner = winning
    context = {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": watch, 
        "owner": owner,
        "thewinner": thewinner,
    }
    return render(request, "auctions/closebids.html", context)


def category(request):
    listings = None
    category = None
    if request.method == "POST":
        category = request.POST["categories"]
        listings = Listing.objects.filter(category = category)
    context = {
        "categories": Category.objects.all(),
        "category": Category.objects.get(id = category).category 
            if category != None else "", 
        "listings": listings,
    }
    return render(request, "auctions/categories.html", context)

@login_required
def watchList(request, userId):
    listOfIds = Watchlist.objects.filter(user = request.user, watching=True).values('listing')
    listing = Listing.objects.filter(id__in = listOfIds)
    return render(request, "auctions/watchlist.html", {"listings": listing})

@login_required
def createListing(request):
    if request.method == "POST":
        form = whenCreatingListingForms(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            desc = form.cleaned_data["desc"]
            bid = form.cleaned_data["bid"]
            imgLink = form.cleaned_data["imgLink"]
            user = request.user
            categoryId = Category.objects.get(id=request.POST["categories"])
            Listing.objects.create(user = user, title = title, desc = desc, price = bid, imgLink = imgLink, category = categoryId)
        return HttpResponseRedirect(reverse('index'))
    else:
        context = {
            "listingForm": whenCreatingListingForms(),
            "categories": Category.objects.all(),
        }
        return render(request, "auctions/createlisting.html", context)

