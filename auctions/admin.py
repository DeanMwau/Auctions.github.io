from django.contrib import admin
from .models import Listings, Bids, Comments, User, Watchlists, UserProfile

# Customizes how models are displayed and managed in the admin interface
class ListingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', "starting_price", 'current_price', 'date_listed', 'status')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')

class BidsAdmin(admin.ModelAdmin):
    list_display = ('auction', 'bidder', 'bid_amount', 'bid_date')
    list_filter = ('auction',)
    search_fields = ('bidder__username', 'auction__title')

class CommentsAdmin(admin.ModelAdmin):
    list_display = ('auction', 'user', 'comment_date')
    list_filter = ('auction',)
    search_fields = ('comment', 'user__username')

class WatchlistsAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'added_at')

# Register your models here.
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Listings, ListingsAdmin)
admin.site.register(Bids, BidsAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Watchlists, WatchlistsAdmin)
