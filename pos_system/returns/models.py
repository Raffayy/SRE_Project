"""
Return models for POS System
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Return(models.Model):
    """
    Return model - represents a return transaction (POH - Point of Handling)
    
    Validates: Requirements 5.1, 6.4
    """
    
    original_sale = models.ForeignKey(
        'sales.Sale',
        on_delete=models.PROTECT,
        related_name='returns',
        null=True,
        blank=True,
        help_text="Original sale (if returning from sale)"
    )
    
    original_rental = models.ForeignKey(
        'rentals.Rental',
        on_delete=models.PROTECT,
        related_name='returns',
        null=True,
        blank=True,
        help_text="Original rental (if returning from rental)"
    )
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='returns',
        help_text="Employee who processed the return"
    )
    
    return_timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the return was processed"
    )
    
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount refunded to customer"
    )
    
    late_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Late fee charged (for rental returns)"
    )
    
    reason = models.TextField(
        blank=True,
        help_text="Reason for return"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'returns'
        ordering = ['-return_timestamp']
        verbose_name = 'Return'
        verbose_name_plural = 'Returns'
        indexes = [
            models.Index(fields=['-return_timestamp']),
            models.Index(fields=['employee']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(original_sale__isnull=False) | models.Q(original_rental__isnull=False),
                name='return_must_have_original'
            )
        ]
    
    def __str__(self):
        if self.original_sale:
            return f"Return #{self.id} for Sale #{self.original_sale.id} - ${self.refund_amount}"
        else:
            return f"Return #{self.id} for Rental #{self.original_rental.id} - ${self.refund_amount}"
    
    def is_rental_return(self):
        """Check if this is a rental return"""
        return self.original_rental is not None
    
    def is_sale_return(self):
        """Check if this is a sale return"""
        return self.original_sale is not None
    
    def calculate_refund(self):
        """Calculate refund amount based on returned items"""
        total_refund = sum(item.line_total for item in self.items.all())
        
        # Subtract late fee if applicable
        if self.is_rental_return() and self.late_fee > 0:
            total_refund -= self.late_fee
        
        self.refund_amount = max(total_refund, Decimal('0.00'))
        self.save()
    
    def complete_return(self):
        """Complete return and restore inventory"""
        # Update inventory for each returned item
        for return_item in self.items.all():
            return_item.item.update_stock(return_item.quantity)
            
            # Create inventory adjustment record
            from inventory.models import InventoryAdjustment
            InventoryAdjustment.objects.create(
                item=return_item.item,
                adjustment_type='RETURN',
                quantity_change=return_item.quantity,
                previous_quantity=return_item.item.stock_quantity - return_item.quantity,
                new_quantity=return_item.item.stock_quantity,
                reason=f"Return #{self.id}",
                adjusted_by=self.employee
            )
        
        # Update original rental status if applicable
        if self.original_rental:
            self.original_rental.status = 'RETURNED'
            self.original_rental.save()


class ReturnItem(models.Model):
    """
    Individual items in a return
    """
    
    return_transaction = models.ForeignKey(
        Return,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        related_name='return_items'
    )
    
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity returned"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price per unit (from original transaction)"
    )
    
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total refund for this line"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'return_items'
        ordering = ['id']
        verbose_name = 'Return Item'
        verbose_name_plural = 'Return Items'
    
    def __str__(self):
        return f"{self.quantity}x {self.item.name} @ ${self.unit_price}"
    
    def save(self, *args, **kwargs):
        """Calculate line total before saving"""
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)
