from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Sale, SaleItem

class ISaleRepository(ABC):
    @abstractmethod
    def save(self, sale: Sale) -> Sale:
        pass
    
    @abstractmethod
    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        pass

class SaleRepository(ISaleRepository):
    def save(self, sale: Sale) -> Sale:
        sale.save()
        return sale
        
    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        try:
            return Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            return None
