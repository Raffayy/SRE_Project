from abc import ABC, abstractmethod
from typing import List, Optional
from django.db import transaction
from .models import Item

class IItemRepository(ABC):
    """Repository interface for Item data access"""
    
    @abstractmethod
    def find_all(self) -> List[Item]:
        """Retrieve all items from storage"""
        pass
    
    @abstractmethod
    def find_by_id(self, item_id: int) -> Optional[Item]:
        """Find item by ID"""
        pass
    
    @abstractmethod
    def save(self, item: Item) -> Item:
        """Save or update an item"""
        pass
    
    @abstractmethod
    def update_stock(self, item_id: int, quantity: int) -> None:
        """Update item stock quantity"""
        pass

class ItemRepository(IItemRepository):
    """Concrete implementation using Django ORM"""
    
    def find_all(self) -> List[Item]:
        """Retrieve all items from database"""
        return list(Item.objects.all())
    
    def find_by_id(self, item_id: int) -> Optional[Item]:
        """Find item by ID"""
        try:
            return Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return None
    
    def save(self, item: Item) -> Item:
        """Save or update an item"""
        item.save()
        return item
    
    @transaction.atomic
    def update_stock(self, item_id: int, quantity: int) -> None:
        """Update item stock quantity atomically"""
        item = Item.objects.select_for_update().get(id=item_id)
        item.stock_quantity = quantity
        item.save()
