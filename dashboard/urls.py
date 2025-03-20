from django.urls import path
from . import views

urlpatterns = [
    # Main dashboard views
    path('', views.index, name='index'),
    path('product/', views.product_analysis, name='product_analysis'),
    path('bidders/', views.bidders_analysis, name='bidders_analysis'),
    path('daily/', views.daily_analysis, name='daily_analysis'),
    
    # API endpoints
    path('export/', views.export_data, name='export_data'),
    path('api/auction-data/', views.get_auction_data, name='get_auction_data'),
]