from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from sales.models import Sale
from inventory.models import Item
from rentals.models import Rental

def dashboard(request):
    """Dashboard view with real data"""
    today = timezone.now().date()
    
    # Sales Stats
    today_sales = Sale.objects.filter(sale_timestamp__date=today, status='COMPLETED')
    daily_revenue = today_sales.aggregate(Sum('total'))['total__sum'] or 0
    daily_transactions = today_sales.count()
    
    # Inventory Stats
    low_stock_count = Item.objects.filter(stock_quantity__lte=10).count()
    
    # Rental Stats
    active_rentals = Rental.objects.filter(status='ACTIVE').count()
    
    # Recent Activity (Sales and Rentals mixed)
    recent_sales = Sale.objects.all().order_by('-sale_timestamp')[:5]

    # Return Stats
    from returns.models import Return
    today_returns = Return.objects.filter(return_timestamp__date=today)
    daily_refunds = today_returns.aggregate(Sum('refund_amount'))['refund_amount__sum'] or 0
    
    # Net Revenue
    from decimal import Decimal
    daily_revenue = daily_revenue - (daily_refunds or Decimal('0.00'))
    
    # Total Transactions (Sales + Returns)
    returns_count = today_returns.count()
    daily_transactions = daily_transactions + returns_count
    


    context = {
        'daily_revenue': daily_revenue,
        'daily_transactions': daily_transactions,
        'low_stock_count': low_stock_count,
        'active_rentals': active_rentals,
        'recent_sales': recent_sales,
        'daily_returns_amount': daily_refunds,
        'returns_count': returns_count
    }
    
    return render(request, 'index.html', context)
