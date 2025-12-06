"""
Rental models for POS System
"""
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal
from datetime import datetime, timedelta


class Rental(models.Model):
    """
    Rental model - represents a rental transaction (POR - Point of Rental)
    
    Validates: Requirements 5.1, 6.4
    """
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='rentals',
        help_text="Employee who processed the rental"
    )
    
    customer_phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Phone number must be exactly 10 digits'
            )
        ],
        help_text="Customer phone number (10 digits)"
    )
    
    rental_timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the rental was made"
    )
    
    due_date = models.DateTimeField(
        help_text="When items should be returned"
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total rental cost"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rentals'
        ordering = ['-rental_timestamp']
        verbose_name = 'Rental'
        verbose_name_plural = 'Rentals'
        indexes = [
            models.Index(fields=['-rental_timestamp']),
            models.Index(fields=['customer_phone']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"Rental #{self.id} - {self.customer_phone} - ${self.total}"
    
    def is_overdue(self):
        """Check if rental is overdue"""
        return datetime.now() > self.due_date and self.status == 'ACTIVE'
    
    def days_overdue(self):
        """Calculate how many days overdue"""
        if not self.is_overdue():
            return 0
        delta = datetime.now() - self.due_date
        return delta.days
    
    def calculate_late_fee(self, late_fee_rate=0.10):
        """Calculate late fee (10% of item price per day)"""
        if not self.is_overdue():
            return Decimal('0.00')
        
        days = self.days_overdue()
        total_late_fee = Decimal('0.00')
        
        for rental_item in self.items.all():
            item_late_fee = rental_item.unit_price * Decimal(str(late_fee_rate)) * days
            total_late_fee += item_late_fee
        
        return total_late_fee
    
    def complete_rental(self):
        """Mark rental as completed and update inventory"""
        if self.status != 'ACTIVE':
            raise ValueError("Rental is not active")
        
        # Update inventory for each item
        for rental_item in self.items.all():
            rental_item.item.update_stock(-rental_item.quantity)
            
            # Create inventory adjustment record
            from inventory.models import InventoryAdjustment
            InventoryAdjustment.objects.create(
                item=rental_item.item,
                adjustment_type='RENTAL',
                quantity_change=-rental_item.quantity,
                previous_quantity=rental_item.item.stock_quantity + rental_item.quantity,
                new_quantity=rental_item.item.stock_quantity,
                reason=f"Rental #{self.id}",
                adjusted_by=self.employee
            )
        
        self.save()


class RentalItem(models.Model):
    """
    Individual items in a rental
    """
    
    rental = models.ForeignKey(
        Rental,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    item = models.ForeignKey(
        'inventory.Item',
        on_delete=models.PROTECT,
        related_name='rental_items'
    )
    
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity rented"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Rental price per unit"
    )
    
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total for this line"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rental_items'
        ordering = ['id']
        verbose_name = 'Rental Item'
        verbose_name_plural = 'Rental Items'
    
    def __str__(self):
        return f"{self.quantity}x {self.item.name} @ ${self.unit_price}"
    
    def save(self, *args, **kwargs):
        """Calculate line total before saving"""
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)
