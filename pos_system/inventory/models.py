"""
Inventory models for POS System
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Item(models.Model):
    """
    Item model - represents products in inventory
    
    Validates: Requirements 5.1, 6.4
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Item name"
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Item price (must be positive)"
    )
    
    stock_quantity = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Current stock quantity (cannot be negative)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When item was added to inventory"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When item was last updated"
    )
    
    class Meta:
        db_table = 'items'
        ordering = ['name']
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['stock_quantity']),
        ]
    
    def __str__(self):
        return f"{self.name} (${self.price}) - Stock: {self.stock_quantity}"
    
    def is_in_stock(self):
        """Check if item is in stock"""
        return self.stock_quantity > 0
    
    def is_low_stock(self, threshold=10):
        """Check if item is low on stock"""
        return 0 < self.stock_quantity <= threshold
    
    def can_fulfill_quantity(self, quantity):
        """Check if we have enough stock for requested quantity"""
        return self.stock_quantity >= quantity
    
    def update_stock(self, quantity_change):
        """
        Update stock quantity
        Positive for additions (returns), negative for subtractions (sales)
        """
        new_quantity = self.stock_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(f"Insufficient stock. Available: {self.stock_quantity}, Requested: {abs(quantity_change)}")
        self.stock_quantity = new_quantity
        self.save()
    
    def calculate_line_total(self, quantity):
        """Calculate total price for given quantity"""
        return self.price * quantity


class InventoryAdjustment(models.Model):
    """
    Track inventory adjustments for audit purposes
    """
    
    ADJUSTMENT_TYPES = [
        ('SALE', 'Sale'),
        ('RETURN', 'Return'),
        ('RENTAL', 'Rental'),
        ('MANUAL', 'Manual Adjustment'),
        ('DAMAGE', 'Damage/Loss'),
    ]
    
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='adjustments'
    )
    
    adjustment_type = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_TYPES
    )
    
    quantity_change = models.IntegerField(
        help_text="Positive for additions, negative for subtractions"
    )
    
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    
    reason = models.TextField(
        blank=True,
        help_text="Reason for adjustment"
    )
    
    adjusted_by = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_adjustments'
    )
    
    adjusted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_adjustments'
        ordering = ['-adjusted_at']
        verbose_name = 'Inventory Adjustment'
        verbose_name_plural = 'Inventory Adjustments'
    
    def __str__(self):
        return f"{self.item.name}: {self.quantity_change:+d} ({self.adjustment_type})"
