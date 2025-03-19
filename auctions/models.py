from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    location = models.CharField(max_length=255, blank=True, null=True)  

    def save(self, *args, **kwargs):
        self.location = self.location.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.location:
            return f"{self.user.username} located at {self.location}"
        else:
            return f"{self.user.username}"

class Listings(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image_urls = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=64)
    category = models.CharField(max_length=64, blank=True, null=True) 
    date_listed = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def clean(self):
        super().clean()  
        if self.starting_price < 0:
            raise ValidationError("Starting price cannot be negative.")
        
    def save(self, *args, **kwargs):
        self.category = self.category.strip()
        self.location = self.location.strip()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Listings"


    def __str__(self):
        return f"{self.title} listed by {self.seller.username} on {self.date_listed}"
    
    @property
    def highest_bid(self):
        highest_bid = self.bids.order_by('-bid_amount').first()
        return highest_bid.bid_amount if highest_bid else None
    
class Bids(models.Model):
    # Related names allows you to access all bids related to a listing using listing_instance.bids.all()
    auction = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids") 
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Bids"

    def clean(self): #add clean method
        super().clean()
        if self.bid_amount < self.auction.current_price:
            raise ValidationError("Bid amount must be at least as large as the starting price.")
        
        if self.bidder == self.auction.seller:
            raise ValidationError("You cannot bid on your own listing.")
        
    def save(self, *args, **kwargs): # add save method
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bid {self.id}: Bidder {self.bidder.username} - Auction {self.auction_id} - ${self.bid_amount}"
    

class Comments(models.Model):
    auction = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment {self.id}: User {self.user.username} - Auction {self.auction_id}"
    
    
class Watchlists(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    #prevent duplicate entries
    class Meta:
        unique_together = ('user', 'listing')
        verbose_name_plural = "Watchlists" 

    def clean(self):
        if self.user == self.listing.seller:
            raise ValidationError("You cannot add your own listing to a watchlist.")
            




