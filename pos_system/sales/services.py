from decimal import Decimal
from typing import List, Dict, Optional
from django.db import transaction
from .models import Sale, SaleItem
from .repositories import ISaleRepository
from inventory.services import InventoryService
from employees.models import Employee

class SalesService:
    def __init__(self, sale_repository: ISaleRepository, inventory_service: InventoryService):
        self.sale_repository = sale_repository
        self.inventory_service = inventory_service
        from employees.services import AuditLogger
        self.audit_logger = AuditLogger()
        
    @transaction.atomic
    def process_sale(self, cashier: Employee, items_data: List[Dict[str, int]]) -> Sale:
        """
        Process a new sale transaction
        items_data: List of dicts with 'item_id' and 'quantity'
        """
        # 1. Create Sale record (Pending)
        sale = Sale(
            employee=cashier,
            subtotal=Decimal('0.00'),
            tax=Decimal('0.00'),
            total=Decimal('0.00'),
            status='PENDING'
        )
        sale.save()
        
        subtotal = Decimal('0.00')
        
        # 2. Process items
        for item_data in items_data:
            item_id = item_data['item_id']
            quantity = item_data['quantity']
            
            # Get item details (price)
            item = self.inventory_service.get_item_by_id(item_id)
            if not item:
                raise ValueError(f"Item {item_id} not found")
                
            # Check stock
            if not self.inventory_service.check_stock_availability(item_id, quantity):
                raise ValueError(f"Insufficient stock for {item.name}")
                
            # Create SaleItem
            sale_item = SaleItem(
                sale=sale,
                item=item,
                quantity=quantity,
                unit_price=item.price
            )
            sale_item.save() # This calculates line_total automatically
            
            subtotal += sale_item.line_total
            
        # 3. Update Sale totals
        sale.subtotal = subtotal
        sale.calculate_totals() # Calculates tax and total
        
        # 4. Complete Sale (updates inventory)
        sale.complete_sale()
        
        # 5. Log Transaction
        try:
            self.audit_logger.log_transaction(cashier.name, "SALE", str(sale.total))
        except Exception as e:
            print(f"Failed to log audit: {e}")
        
        return sale

class TransactionRecoveryService:
    """Handles recovery of interrupted transactions"""
    
    def __init__(self, temp_file_path: str = 'temp_transaction.json'):
        self.temp_file_path = temp_file_path
        
    def save_temp_transaction(self, data: dict):
        import json
        with open(self.temp_file_path, 'w') as f:
            json.dump(data, f)
            
    def recover_transaction(self) -> Optional[Dict]:
        import json
        import os
        if os.path.exists(self.temp_file_path):
            try:
                with open(self.temp_file_path, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
        
    def clear_temp_transaction(self):
        import os
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

