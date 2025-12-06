from django.test import TestCase
from decimal import Decimal
from .models import Item
from .repositories import ItemRepository
from .services import InventoryService

class InventoryServiceTests(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            name="Test Item",
            price=Decimal("10.00"),
            stock_quantity=50
        )
        self.repo = ItemRepository()
        self.service = InventoryService(self.repo)
        
    def test_get_all_items(self):
        items = self.service.get_all_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, "Test Item")
        
    def test_check_stock_availability(self):
        self.assertTrue(self.service.check_stock_availability(self.item.id, 10))
        self.assertFalse(self.service.check_stock_availability(self.item.id, 100))
        
    def test_update_stock_sale(self):
        transaction_items = [{'item_id': self.item.id, 'quantity': 5}]
        self.service.update_stock_for_transaction(transaction_items, is_sale=True)
        
        updated_item = self.repo.find_by_id(self.item.id)
        self.assertEqual(updated_item.stock_quantity, 45)
        
    def test_update_stock_return(self):
        transaction_items = [{'item_id': self.item.id, 'quantity': 5}]
        self.service.update_stock_for_transaction(transaction_items, is_sale=False)
        
        updated_item = self.repo.find_by_id(self.item.id)
        self.assertEqual(updated_item.stock_quantity, 55)
        
    def test_insufficient_stock(self):
        transaction_items = [{'item_id': self.item.id, 'quantity': 100}]
        with self.assertRaises(ValueError):
            self.service.update_stock_for_transaction(transaction_items, is_sale=True)
