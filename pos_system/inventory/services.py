from typing import List, Optional
from .models import Item
from .repositories import IItemRepository

class InventoryService:
    """Business logic for inventory management"""
    
    def __init__(self, item_repository: IItemRepository):
        self.item_repository = item_repository
    
    def get_all_items(self) -> List[Item]:
        """Get all items in inventory"""
        return self.item_repository.find_all()
    
    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """Get specific item"""
        return self.item_repository.find_by_id(item_id)
    
    def update_stock_for_transaction(self, transaction_items: List[dict], is_sale: bool) -> None:
        """
        Update inventory for a transaction
        transaction_items: List of dicts with 'item_id' and 'quantity'
        """
        for trans_item in transaction_items:
            item_id = trans_item['item_id']
            quantity = trans_item['quantity']
            
            current_item = self.item_repository.find_by_id(item_id)
            
            if current_item is None:
                raise ValueError(f"Item {item_id} not found")
            
            if is_sale:
                new_quantity = current_item.stock_quantity - quantity
            else:  # Return
                new_quantity = current_item.stock_quantity + quantity
            
            if new_quantity < 0:
                raise ValueError(f"Insufficient stock for item {item_id}")
            
            self.item_repository.update_stock(item_id, new_quantity)

    def check_stock_availability(self, item_id: int, quantity: int) -> bool:
        """Check if enough stock is available"""
        item = self.item_repository.find_by_id(item_id)
        if item and item.stock_quantity >= quantity:
            return True
        return False
