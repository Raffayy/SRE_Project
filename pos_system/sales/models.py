"""
Sales models for POS System
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Sale(models.Model):
    """
    Sale model - represents a sales transaction
    
    Validates: Requirements 5.1, 6.4
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='sales',
        help_text="Employee who processed the sale"
    )
    
    sale_timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the sale was made"
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total before tax"
    )
    
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Tax amount (6%)"
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total amount including tax"
    )
    
    discount_applied = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Discount amount (if coupon used)"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sales'
        ordering = ['-sale_timestamp']
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'
        indexes = [
            models.Index(fields=['-sale_timestamp']),
            models.Index(fields=['employee', '-sale_timestamp']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Sale #{self.id} - ${self.total} by {self.employee.username}"
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total from sale items"""
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.tax = self.subtotal * Decimal('0.06')  # 6% tax rate
        self.total = self.subtotal + self.tax - self.discount_applied
        self.save()
    
    def apply_discount(self, discount_percentage=10):
        """Apply discount (default 10% for coupons)"""
        discount_amount = self.subtotal * (Decimal(discount_percentage) / Decimal('100'))
        self.discount_applied = discount_amount
        self.calculate_totals()
    
    def complete_sale(self):
        """Mark sale as completed and update inventory"""
        if self.status == 'COMPLETED':
            raise ValueError("Sale is already completed")
        
        # Update inventory for each item
        for sale_item in self.items.all():
            sale_item.item.update_stock(-sale_item.quantity)
            
            # Create inventory adjustment record
            from inventory.models import InventoryAdjustment
            InventoryAdjustment.objects.create(
                item=sale_item.item,
                adjustment_type='SALE',
                quantity_change=-sale_item.quantity,
                previous_quantity=sale_item.item.stock_quantity + sale_item.quantity,
                new_quantity=sale_item.item.stock_quantity,
                reason=f"Sale #{self.id}",
                adjusted_by=self.employee
            )
        
        self.status = 'COMPLETED'
        self.save()


class SaleItem(models.Model):
    """
    Individual items in a sale
    """
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        related_name='sale_items'
    )
    
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity sold"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price per unit at time of sale"
    )
    
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total for this line (quantity × unit_price)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sale_items'
        ordering = ['id']
        verbose_name = 'Sale Item'
        verbose_name_plural = 'Sale Items'
    
    def __str__(self):
        return f"{self.quantity}x {self.item.name} @ ${self.unit_price}"
    
    def save(self, *args, **kwargs):
        """Calculate line total before saving"""
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)
