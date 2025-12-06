from django.contrib import admin
from .models import Return, ReturnItem


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 1
    readonly_fields = ['line_total']


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'return_timestamp', 'refund_amount', 'late_fee', 'get_original']
    list_filter = ['return_timestamp', 'employee']
    search_fields = ['id', 'employee__username', 'reason']
    readonly_fields = ['return_timestamp', 'created_at']
    inlines = [ReturnItemInline]
    
    fieldsets = (
        ('Return Information', {
            'fields': ('employee', 'original_sale', 'original_rental', 'reason')
        }),
        ('Amounts', {
            'fields': ('refund_amount', 'late_fee')
        }),
        ('Timestamps', {
            'fields': ('return_timestamp', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_original(self, obj):
        if obj.original_sale:
            return f"Sale #{obj.original_sale.id}"
        elif obj.original_rental:
            return f"Rental #{obj.original_rental.id}"
        return "N/A"
    get_original.short_description = 'Original Transaction'


@admin.register(ReturnItem)
class ReturnItemAdmin(admin.ModelAdmin):
    list_display = ['return_transaction', 'item', 'quantity', 'unit_price', 'line_total']
    list_filter = ['created_at']
    search_fields = ['item__name', 'return_transaction__id']
    readonly_fields = ['line_total', 'created_at']
