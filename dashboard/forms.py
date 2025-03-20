from django import forms
from .models import Auction

class AuctionSearchForm(forms.Form):
    auction_id = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter auction ID',
            'id': 'auction-id-input'
        })
    )
    
class ProductSearchForm(forms.Form):
    auction_id = forms.CharField(
        max_length=255, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter auction ID',
            'id': 'auction-id-input'
        })
    )
    
class DateSearchForm(forms.Form):
    auction_id = forms.CharField(
        max_length=255, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter auction ID',
            'id': 'auction-id-input'
        })
    )
    # Remove the date field since we'll use clickable dates instead