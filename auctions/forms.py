from django import forms
from .models import UserProfile, Listings
from django.contrib.auth.models import User


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="First Name", max_length=30, required=False)
    last_name = forms.CharField(label="Last Name", max_length=30, required=False)
    location = forms.CharField(label="Location", max_length=255, required=False) 
    
    class Meta:
        model = UserProfile
        fields = ['location']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['location'].initial = self.instance.location 

class ChangeEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ['title', 'description', 'starting_price', 'current_price', 'image_urls', 'location', 'category']