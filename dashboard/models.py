from django.db import models

class Auction(models.Model):
    shopify_auction_id = models.CharField(max_length=255, primary_key=True)
    auction_name = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Auction {self.shopify_auction_id}"
    
    class Meta:
        db_table = 'auctions'
        managed = False  # Since we're using an existing database

class AuctionProduct(models.Model):
    id = models.AutoField(primary_key=True)
    shopify_auction = models.ForeignKey(Auction, on_delete=models.CASCADE, db_column='shopify_auction_id')
    product_id = models.CharField(max_length=255)
    winning_cusotmer = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"Product {self.product_id} in Auction {self.shopify_auction_id}"
    
    class Meta:
        db_table = 'auction_relation_with_products'
        managed = False  # Since we're using an existing database

class BidRecord(models.Model):
    id = models.AutoField(primary_key=True)
    auction_shopify_id = models.CharField(max_length=255)
    product_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bidding_datetime = models.DateTimeField()
    bid_type = models.CharField(max_length=50)  # 'auto' or 'manual'
    user_city = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"Bid {self.id} for Product {self.product_id}"
    
    class Meta:
        db_table = 'bid_records'
        managed = False  # Since we're using an existing database