import pandas as pd
import json
from django.db import connection
from datetime import datetime, timedelta
from decimal import Decimal

# Custom JSON encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

# Helper function to convert Decimal objects to float for JSON serialization
def decimal_to_float(data):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, dict):
        return {k: decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [decimal_to_float(item) for item in data]
    return data

def get_auction_summary(auction_id):
    """Get summary statistics for an auction"""
    with connection.cursor() as cursor:
        # Get total products related to the specific auction_id
        cursor.execute("""
            SELECT COUNT(*) as total_products
            FROM auction_relation_with_products
            WHERE shopify_auction_id = %s
        """, [auction_id])
        result = cursor.fetchone()
        total_products = result[0] if result else 0
        
        # Debug: Print the query and result
        # print(f"Total products query for auction {auction_id}: {total_products}")
        
        # Try alternative query if total_products is 0
        if total_products == 0:
            # Try with different column name or format
            cursor.execute("""
                SELECT COUNT(DISTINCT product_id) as total_products
                FROM bid_records
                WHERE auction_shopify_id = %s
            """, [auction_id])
            result = cursor.fetchone()
            total_products = result[0] if result else 0
            # print(f"Alternative query for total products: {total_products}")
        
        # Get total bids related to the auction
        cursor.execute("""
            SELECT COUNT(*) as total_bids
            FROM bid_records
            WHERE auction_shopify_id = %s
        """, [auction_id])
        total_bids = cursor.fetchone()[0]
        
        # Get winning bids related to the auction
        cursor.execute("""
            SELECT COUNT(*) as winning_products
            FROM auction_relation_with_products
            WHERE shopify_auction_id = %s AND winning_cusotmer IS NOT NULL
        """, [auction_id])
        winning_products = cursor.fetchone()[0]
        
        # Get auto vs manual bids related to the auction
        cursor.execute("""
            SELECT bid_type, COUNT(*) as count
            FROM bid_records
            WHERE auction_shopify_id = %s
            GROUP BY bid_type
        """, [auction_id])
        bid_types = {row[0]: row[1] for row in cursor.fetchall()}
        auto_bids = bid_types.get('auto', 0)
        manual_bids = bid_types.get('manual', 0)
        
    summary = {
        'total_products': total_products,
        'total_bids': total_bids,
        'winning_products': winning_products,
        'not_winning_products': total_products - winning_products,
        'auto_bids': auto_bids,
        'manual_bids': manual_bids
    }
    
    # print(f"Summary for auction {auction_id}: {summary}")
    return summary

def get_auto_vs_manual_data(auction_id):
    """Get auto vs manual bids over time"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                DATE(bidding_datetime) as bid_date,
                SUM(CASE WHEN bid_type = 'auto' THEN 1 ELSE 0 END) as auto,
                SUM(CASE WHEN bid_type = 'manual' THEN 1 ELSE 0 END) as manual
            FROM bid_records
            WHERE auction_shopify_id = %s
            GROUP BY DATE(bidding_datetime)
            ORDER BY bid_date
        """, [auction_id])
        data = dictfetchall(cursor)
        
    # Convert to format needed for Chart.js
    for item in data:
        item['bid_date'] = item['bid_date'].strftime('%Y-%m-%d')
        
    return data

def get_daily_bid_data(auction_id):
    """Get daily bid statistics"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                DATE(bidding_datetime) as bid_date,
                COUNT(*) as total_bids,
                COUNT(DISTINCT user_id) as unique_users
            FROM bid_records
            WHERE auction_shopify_id = %s
            GROUP BY DATE(bidding_datetime)
            ORDER BY bid_date
        """, [auction_id])
        data = dictfetchall(cursor)
        
    # Convert to format needed for Chart.js
    for item in data:
        item['bid_date'] = item['bid_date'].strftime('%Y-%m-%d')
        
    return data

def get_top_bidders(auction_id, limit=10):
    """Get top bidders with comprehensive statistics"""
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH bidder_products AS (
                -- Get all products bid on by each user
                SELECT 
                    br.user_id,
                    br.product_id,
                    COUNT(*) AS bid_count
                FROM bid_records br
                WHERE br.auction_shopify_id = %s
                GROUP BY br.user_id, br.product_id
            ),
            product_status AS (
                -- Get the status and winner of each product
                SELECT 
                    p.id AS product_id,
                    p.final_selling_status,
                    p.user_id AS winner_id
                FROM products p
                WHERE p.auction_shopify_id = %s
            ),
            bidder_stats AS (
                -- Calculate statistics for each bidder
                SELECT 
                    bp.user_id,
                    COUNT(DISTINCT bp.product_id) AS total_products,
                    SUM(bp.bid_count) AS total_bids,
                    COUNT(DISTINCT CASE WHEN ps.final_selling_status = 'sold' AND ps.winner_id = bp.user_id THEN bp.product_id END) AS win_products,
                    SUM(CASE WHEN ps.final_selling_status = 'sold' AND ps.winner_id = bp.user_id THEN bp.bid_count ELSE 0 END) AS win_bids,
                    SUM(CASE WHEN ps.final_selling_status = 'sold' AND ps.winner_id IS NOT NULL AND ps.winner_id != bp.user_id THEN bp.bid_count ELSE 0 END) AS lost_bids,
                    SUM(CASE WHEN ps.final_selling_status != 'sold' OR ps.winner_id IS NULL THEN bp.bid_count ELSE 0 END) AS pending_bids
                FROM bidder_products bp
                LEFT JOIN product_status ps ON bp.product_id = ps.product_id
                GROUP BY bp.user_id
            )
            
            -- Get final results
            SELECT 
                user_id,
                total_products,
                win_products,
                total_bids,
                win_bids,
                lost_bids,
                pending_bids
            FROM bidder_stats
            ORDER BY total_bids DESC
            LIMIT %s
        """, [auction_id, auction_id, limit])
        data = dictfetchall(cursor)
        
    # Calculate win rate (as percentage of products won out of total products bid on)
    for bidder in data:
        if bidder['total_products'] > 0:
            bidder['win_rate'] = (bidder['win_products'] / bidder['total_products']) * 100
        else:
            bidder['win_rate'] = 0
            
    return data

def get_top_products(auction_id, limit=10):
    """Get top products by bid count with auto/manual breakdown"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                product_id,
                COUNT(*) as total_bids,
                SUM(CASE WHEN bid_type = 'auto' THEN 1 ELSE 0 END) as auto,
                SUM(CASE WHEN bid_type = 'manual' THEN 1 ELSE 0 END) as manual
            FROM bid_records
            WHERE auction_shopify_id = %s
            GROUP BY product_id
            ORDER BY total_bids DESC
            LIMIT %s
        """, [auction_id, limit])
        data = dictfetchall(cursor)
        
    return data

def get_product_details(auction_id, product_id):
    """Get detailed information about a specific product"""
    with connection.cursor() as cursor:
        # Get basic product stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_bids,
                MAX(bid_amount) as highest_bid,
                COUNT(DISTINCT user_id) as unique_bidders
            FROM bid_records
            WHERE auction_shopify_id = %s AND product_id = %s
        """, [auction_id, product_id])
        basic_stats = dictfetchall(cursor)[0]
        
        # Convert Decimal to float for JSON serialization
        if isinstance(basic_stats['highest_bid'], Decimal):
            basic_stats['highest_bid'] = float(basic_stats['highest_bid'])
        
        # Get bid history
        cursor.execute("""
            SELECT 
                DATE(bidding_datetime) as date,
                SUM(CASE WHEN bid_type = 'auto' THEN 1 ELSE 0 END) as auto,
                SUM(CASE WHEN bid_type = 'manual' THEN 1 ELSE 0 END) as manual
            FROM bid_records
            WHERE auction_shopify_id = %s AND product_id = %s
            GROUP BY DATE(bidding_datetime)
            ORDER BY date
        """, [auction_id, product_id])
        bid_history = dictfetchall(cursor)
        
        # Convert dates to strings for JSON serialization
        for item in bid_history:
            item['date'] = item['date'].strftime('%Y-%m-%d')
        
        # Get top bidders for this product
        cursor.execute("""
            SELECT 
                user_id,
                COUNT(*) as bids,
                MAX(bid_amount) as highest_bid
            FROM bid_records
            WHERE auction_shopify_id = %s AND product_id = %s
            GROUP BY user_id
            ORDER BY bids DESC
            LIMIT 5
        """, [auction_id, product_id])
        top_bidders = dictfetchall(cursor)
        
        # Convert Decimal to float for JSON serialization
        for bidder in top_bidders:
            if isinstance(bidder['highest_bid'], Decimal):
                bidder['highest_bid'] = float(bidder['highest_bid'])
        
    return {
        'basic_stats': basic_stats,
        'bid_history': bid_history,
        'top_bidders': top_bidders
    }

def get_data_for_specific_date(auction_id, date):
    """Get bid data for a specific date"""
    # Convert string date to datetime
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    with connection.cursor() as cursor:
        # Get hourly breakdown
        cursor.execute("""
            SELECT 
                HOUR(bidding_datetime) as hour,
                COUNT(*) as total_bids,
                SUM(CASE WHEN bid_type = 'auto' THEN 1 ELSE 0 END) as auto,
                SUM(CASE WHEN bid_type = 'manual' THEN 1 ELSE 0 END) as manual
            FROM bid_records
            WHERE auction_shopify_id = %s 
              AND DATE(bidding_datetime) = %s
            GROUP BY HOUR(bidding_datetime)
            ORDER BY hour
        """, [auction_id, date])
        hourly_data = dictfetchall(cursor)
        
        # Get product breakdown
        cursor.execute("""
            SELECT 
                product_id,
                COUNT(*) as total_bids
            FROM bid_records
            WHERE auction_shopify_id = %s 
              AND DATE(bidding_datetime) = %s
            GROUP BY product_id
            ORDER BY total_bids DESC
            LIMIT 10
        """, [auction_id, date])
        product_data = dictfetchall(cursor)
        
        # Get user breakdown
        cursor.execute("""
            SELECT 
                user_id,
                COUNT(*) as total_bids
            FROM bid_records
            WHERE auction_shopify_id = %s 
              AND DATE(bidding_datetime) = %s
            GROUP BY user_id
            ORDER BY total_bids DESC
            LIMIT 10
        """, [auction_id, date])
        user_data = dictfetchall(cursor)
        
    return {
        'hourly_data': hourly_data,
        'product_data': product_data,
        'user_data': user_data
    }

def export_to_csv(data, filename):
    """Convert data to CSV format"""
    # Convert Decimal objects to float for CSV export
    data = decimal_to_float(data)
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def get_auction_dates(auction_id):
    """Get all dates with bids for a specific auction, ordered chronologically"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT DATE(bidding_datetime) as bid_date
            FROM bid_records
            WHERE auction_shopify_id = %s
            ORDER BY bid_date
        """, [auction_id])
        dates = [row[0] for row in cursor.fetchall()]
    
    # Convert dates to string format
    formatted_dates = [date.strftime('%Y-%m-%d') for date in dates]
    return formatted_dates

def get_auction_products(auction_id):
    """Get all products for a specific auction, ordered by product_id, including product title"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT br.product_id, p.product_title
            FROM bid_records br
            JOIN products p ON br.product_id = p.id
            WHERE br.auction_shopify_id = %s
            ORDER BY br.product_id
        """, [auction_id])
        products = [{'id': row[0], 'title': row[1]} for row in cursor.fetchall()]
    
    return products

def get_auto_bids_sequence(auction_id):
    """Get auto bids for an auction in chronological sequence"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id,
                product_id,
                user_id,
                bid_amount,
                bidding_datetime
            FROM bid_records
            WHERE auction_shopify_id = %s AND bid_type = 'auto'
            ORDER BY bidding_datetime
            
        """, [auction_id])
        bids = dictfetchall(cursor)
    
    # Convert Decimal objects to float for JSON serialization
    for bid in bids:
        if isinstance(bid['bid_amount'], Decimal):
            bid['bid_amount'] = float(bid['bid_amount'])
        
        # Check if bidding_datetime is a datetime object before formatting
        if hasattr(bid['bidding_datetime'], 'strftime'):
            bid['bidding_datetime'] = bid['bidding_datetime'].strftime('%Y-%m-%d %H:%M:%S')
    
    return bids

def get_all_auctions():
    """Get all available auction IDs along with their created_at timestamp and handle from both tables """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT auction_shopify_id, handle, MAX(created_at) as created_at
            FROM shopify_auction_all_listings
            GROUP BY auction_shopify_id, handle
            ORDER BY created_at DESC
        """)
        auctions = cursor.fetchall()
    return auctions

 

