from django.contrib import admin
from .models import Item, InventoryAdjustment


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'is_in_stock', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Item Information', {
            'fields': ('name', 'price', 'stock_quantity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['item', 'adjustment_type', 'quantity_change', 'adjusted_by', 'adjusted_at']
    list_filter = ['adjustment_type', 'adjusted_at']
    search_fields = ['item__name', 'reason']
    readonly_fields = ['adjusted_at']
    
    def has_add_permission(self, request):
        # Adjustments should be created through transactions, not manually
        return False
