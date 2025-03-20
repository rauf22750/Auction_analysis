from django.contrib import admin
from .models import Auction, AuctionProduct, BidRecord

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('shopify_auction_id', 'auction_name', 'start_date', 'end_date')
    search_fields = ('shopify_auction_id', 'auction_name')

@admin.register(AuctionProduct)
class AuctionProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'shopify_auction', 'product_id', 'winning_cusotmer')
    search_fields = ('product_id', 'shopify_auction__shopify_auction_id')
    list_filter = ('shopify_auction',)

@admin.register(BidRecord)
class BidRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'auction_shopify_id', 'product_id', 'user_id', 'bid_amount', 'bidding_datetime', 'bid_type')
    search_fields = ('auction_shopify_id', 'product_id', 'user_id')
    list_filter = ('bid_type', 'bidding_datetime')