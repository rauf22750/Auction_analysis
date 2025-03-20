import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import AuctionSearchForm, ProductSearchForm, DateSearchForm
from .utils import (
    get_auction_summary, get_auto_vs_manual_data, get_daily_bid_data,
    get_top_bidders, get_top_products, get_product_details,
    get_data_for_specific_date, export_to_csv, DecimalEncoder, decimal_to_float,
    get_auto_bids_sequence, get_auction_products, get_auction_dates, get_all_auctions
)
from datetime import datetime

def index(request):
    """Main dashboard view"""
    form = AuctionSearchForm(request.GET or None)
    auction_id = request.GET.get('auction_id', '660670284157')  # Default auction ID
    
    # Get all available auctions (returns a list of tuples: (auction_shopify_id, handle, created_at))
    all_auctions = get_all_auctions()
    
    # If no auction_id is provided but we have auctions, use the first one
    if not auction_id and all_auctions:
        auction_id = all_auctions[0][0]
        
    # Get data for the dashboard
    summary = get_auction_summary(auction_id)
    auto_vs_manual = get_auto_vs_manual_data(auction_id)
    top_bidders = get_top_bidders(auction_id)
    top_products = get_top_products(auction_id)
    auto_bids = get_auto_bids_sequence(auction_id)

    # Convert data for JSON serialization
    auto_vs_manual = decimal_to_float(auto_vs_manual)
    top_products_json = decimal_to_float(top_products)

    context = {
        'form': form,
        'auction_id': auction_id,
        'all_auctions': all_auctions,
        'summary': summary,
        'auto_vs_manual': json.dumps(auto_vs_manual),
        'top_bidders': top_bidders,
        'top_products': top_products,
        'top_products_json': json.dumps(top_products_json),
        'auto_bids': auto_bids,
        'active_tab': 'overview'
    }
    
    return render(request, 'dashboard/index.html', context)    

def product_analysis(request):
    """Product analysis view"""
    form = ProductSearchForm(request.GET or None)
    auction_id = request.GET.get('auction_id', '660670284157')
    product_id = request.GET.get('product_id', '')
    
    # Get all available auctions
    all_auctions = get_all_auctions()
    
    # If no auction_id is provided but we have auctions, use the first one
    if not auction_id and all_auctions:
        auction_id = all_auctions[0]

    # Get all products for this auction
    auction_products = get_auction_products(auction_id)
    
    # If no product_id is provided but we have products, use the first one
    if not product_id and auction_products:
        product_id = auction_products[0]['id']
    
    context = {
        'form': form,
        'auction_id': auction_id,
        'all_auctions': all_auctions,  # Add all auctions to context
        'product_id': product_id,
        'auction_products': auction_products,
        'active_tab': 'product'
    }
    
    # If product ID is provided, get product details
    if product_id:
        product_details = get_product_details(auction_id, product_id)
        context['product_details'] = product_details
        # Convert bid history for JSON serialization
        bid_history = decimal_to_float(product_details['bid_history'])
        context['bid_history'] = json.dumps(bid_history)
        context['top_bidders'] = product_details['top_bidders']
    
    return render(request, 'dashboard/product.html', context)

def bidders_analysis(request):
    """Top bidders analysis view"""
    form = AuctionSearchForm(request.GET or None)
    
    # Get all available auctions
    all_auctions = get_all_auctions()
    
    # Get auction_id from request or use default
    auction_id = request.GET.get('auction_id')
    
    # If no auction_id is provided but we have auctions, use the first one
    if not auction_id and all_auctions:
        auction_id = all_auctions[0]
    # If still no auction_id, use a default
    elif not auction_id:
        auction_id = '660670284157'  # Default auction ID
    
    # Get top bidders data
    top_bidders = get_top_bidders(auction_id, limit=20)
    
    # Prepare data for JSON serialization and charts
    top_bidders_json = decimal_to_float([
        {
            'id': bidder['user_id'],
            'products': bidder['total_products'],
            'winProducts': bidder['win_products'],
            'totalBids': bidder['total_bids'],
            'winBids': bidder['win_bids'],
            'lostBids': bidder['lost_bids'],
            'pendingBids': bidder['pending_bids'],
            'winRate': bidder['win_rate']
        } for bidder in top_bidders[:10]
    ])
    
    # Prepare chart data
    chart_data = []
    for bidder in top_bidders[:10]:
        chart_data.append({
            'bidder': bidder['user_id'],
            'winBids': bidder['win_bids'],
            'lostBids': bidder['lost_bids'],
            'pendingBids': bidder['pending_bids'],
            'totalBids': bidder['total_bids']
        })
    
    context = {
        'form': form,
        'auction_id': auction_id,
        'all_auctions': all_auctions,
        'top_bidders': top_bidders,
        'top_bidders_json': json.dumps(top_bidders_json),
        'chart_data': json.dumps(decimal_to_float(chart_data)),
        'active_tab': 'bidders'
    }
    
    return render(request, 'dashboard/bidders.html', context)

def daily_analysis(request):
    """Daily bid analysis view"""
    form = DateSearchForm(request.GET or None)
    auction_id = request.GET.get('auction_id', '660670284157')
    date = request.GET.get('date', None)
    
    # Get all available auctions
    all_auctions = get_all_auctions()
    
    # If no auction_id is provided but we have auctions, use the first one
    if not auction_id and all_auctions:
        auction_id = all_auctions[0]
    
    
    # Get all dates with bids for this auction
    auction_dates = get_auction_dates(auction_id)
    
    # If no date is provided but we have dates, use the first one
    if not date and auction_dates:
        date = auction_dates[0]
    
    # Get daily bid data
    daily_data = get_daily_bid_data(auction_id)
    auto_vs_manual = get_auto_vs_manual_data(auction_id)
    
    # Convert data for JSON serialization
    daily_data = decimal_to_float(daily_data)
    auto_vs_manual = decimal_to_float(auto_vs_manual)
    
    context = {
        'form': form,
        'auction_id': auction_id,
        'all_auctions': all_auctions,  # Add all auctions to context
        'date': date,
        'auction_dates': auction_dates,
        'daily_data': json.dumps(daily_data),
        'auto_vs_manual': json.dumps(auto_vs_manual),
        'active_tab': 'daily'
    }
    
    # If date is provided, get specific date data
    if date:
        date_data = get_data_for_specific_date(auction_id, date)
        context['date_data'] = date_data
        # Convert hourly data for JSON serialization
        hourly_data = decimal_to_float(date_data['hourly_data'])
        context['hourly_data'] = json.dumps(hourly_data)
    
    return render(request, 'dashboard/daily.html', context)

@csrf_exempt
def export_data(request):
    """Export data to CSV"""
    data_type = request.POST.get('data_type')
    auction_id = request.POST.get('auction_id')
    
    if data_type == 'top_bidders':
        data = get_top_bidders(auction_id, limit=100)
        filename = f"top_bidders_{auction_id}.csv"
    elif data_type == 'top_products':
        data = get_top_products(auction_id, limit=100)
        filename = f"top_products_{auction_id}.csv"
    elif data_type == 'daily_data':
        data = get_daily_bid_data(auction_id)
        filename = f"daily_data_{auction_id}.csv"
    elif data_type == 'auto_vs_manual':
        data = get_auto_vs_manual_data(auction_id)
        filename = f"auto_vs_manual_{auction_id}.csv"
    elif data_type == 'product_details':
        product_id = request.POST.get('product_id')
        product_details = get_product_details(auction_id, product_id)
        data = product_details['bid_history']
        filename = f"product_{product_id}_auction_{auction_id}.csv"
    else:
        return JsonResponse({'error': 'Invalid data type'}, status=400)
    
    csv_data = export_to_csv(data, filename)
    
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@csrf_exempt
def get_auction_data(request):
    """API endpoint to get auction data for AJAX requests"""
    auction_id = request.GET.get('auction_id')
    data_type = request.GET.get('data_type')
    
    if not auction_id:
        return JsonResponse({'error': 'Auction ID is required'}, status=400)
    
    if data_type == 'summary':
        data = get_auction_summary(auction_id)
    elif data_type == 'auto_vs_manual':
        data = get_auto_vs_manual_data(auction_id)
    elif data_type == 'top_bidders':
        data = get_top_bidders(auction_id)
    elif data_type == 'top_products':
        data = get_top_products(auction_id)
    elif data_type == 'daily_data':
        data = get_daily_bid_data(auction_id)
    else:
        return JsonResponse({'error': 'Invalid data type'}, status=400)
    
    # Convert Decimal objects to float for JSON serialization
    data = decimal_to_float(data)
    
    return JsonResponse(data, safe=False)