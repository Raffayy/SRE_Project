from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .services import SalesService
from .repositories import SaleRepository
from inventory.services import InventoryService
from inventory.repositories import ItemRepository
import json

def pos_view(request):
    """Point of Sale View"""
    # Initialize services
    item_repo = ItemRepository()
    inventory_service = InventoryService(item_repo)
    
    if request.method == 'POST':
        # Handle sale processing
        try:
            data = json.loads(request.body)
            items_data = data.get('items', [])
            
            sale_repo = SaleRepository()
            sales_service = SalesService(sale_repo, inventory_service)
            
            # For demo, using first employee or current user if logged in
            # In real app: request.user.employee
            from employees.models import Employee
            cashier = Employee.objects.first() 
            
            if not cashier:
                return JsonResponse({'success': False, 'error': 'No cashier found'})
                
            sale = sales_service.process_sale(cashier, items_data)
            
            return JsonResponse({
                'success': True, 
                'sale_id': sale.id, 
                'total': str(sale.total)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    # GET request - show POS interface
    items = inventory_service.get_all_items()
    return render(request, 'sales/pos.html', {'items': items})
