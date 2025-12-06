from django.test import TestCase
from decimal import Decimal
from employees.models import Employee
from inventory.models import Item
from inventory.repositories import ItemRepository
from inventory.services import InventoryService
from .models import Sale
from .repositories import SaleRepository
from .services import SalesService

class SalesServiceTests(TestCase):
    def setUp(self):
        self.cashier = Employee.objects.create(
            username="cashier1",
            name="John Doe",
            position="Cashier"
        )
        self.item = Item.objects.create(
            name="Test Item",
            price=Decimal("10.00"),
            stock_quantity=50
        )
        
        self.sale_repo = SaleRepository()
        self.item_repo = ItemRepository()
        self.inventory_service = InventoryService(self.item_repo)
        self.service = SalesService(self.sale_repo, self.inventory_service)
        
    def test_process_sale_success(self):
        items_data = [{'item_id': self.item.id, 'quantity': 2}]
        
        sale = self.service.process_sale(self.cashier, items_data)
        
        self.assertIsNotNone(sale.id)
        self.assertEqual(sale.subtotal, Decimal("20.00"))
        self.assertEqual(sale.total, Decimal("21.20")) # 20.00 + 6% tax
        
        # Check inventory update
        updated_item = self.item_repo.find_by_id(self.item.id)
        self.assertEqual(updated_item.stock_quantity, 48)
        
    def test_process_sale_insufficient_stock(self):
        items_data = [{'item_id': self.item.id, 'quantity': 100}]
        
        with self.assertRaises(ValueError):
            self.service.process_sale(self.cashier, items_data)
            
        # Check inventory unchanged
        updated_item = self.item_repo.find_by_id(self.item.id)
        self.assertEqual(updated_item.stock_quantity, 50)
