from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createListing", views.createListing, name="createListing"),
    path("listing/<str:listingId>", views.listing, name="listing"),
    path("removingWatchlist/<str:listingId>", views.removingWatchlist, name="removingWatchlist"),
    path("addingWatchlist/<str:listingId>", views.addingWatchlist, name="addingWatchlist"),
    path("bid/<str:listingId>", views.bid, name="bid"),
    path("categories", views.category, name="categories"),
    path("closingBid/<str:listingId>", views.closingBid, name="closingBid"),
    path("watchList/<str:userId>", views.watchList, name="watchlist")
]
