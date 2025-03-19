from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("welcome", views.welcome, name="welcome"),
    path("closed", views.closed_listings, name="closed"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create"),
    path("<int:listing_id>/", views.listing_view, name="listing"),
    path("<int:listing_id>/closed", views.closed_listing, name="listingclosed"),
    path("<int:listing_id>/bid/", views.place_bid, name="placebid"),
    path("<int:listing_id>/add/", views.add_watchlist, name="addwatchlist"),
    path("<int:listing_id>/remove/", views.remove_watchlist, name="removewatchlist"),
    path("<int:listing_id>/close/", views.close_bidding, name="closebidding"),
    path("<int:listing_id>/addcomment/", views.add_comment, name="addcomment"),
    path("watchlist", views.watch_list, name="watchlist"),
    path("categories/", views.categories, name="categories"),
    path("category/<str:category_name>/", views.category_listings, name="category_listings"),
    path("seller/<str:username>/listings/", views.user_listings, name="seller"),
    path("account/", views.account, name="account"),
    path("account/change_profile_details/", views.change_profile, name="change_profile"),
    path("account/change_email/", views.change_email, name="change_email"),
    path("account/change_password/", auth_views.PasswordChangeView.as_view(
        template_name='auctions/change_details.html',
        success_url=reverse_lazy('account')  # Redirect to account page after success
    ), name='change_password'),
    path("listings/<int:listing_id>/edit/", views.edit_listing, name="edit_listing"),
    path("listings/<int:listing_id>/delete/", views.delete_listing, name="delete_listing"),
]
