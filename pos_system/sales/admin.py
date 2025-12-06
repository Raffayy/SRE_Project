from django.contrib import admin
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ['line_total']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'sale_timestamp', 'subtotal', 'tax', 'total', 'status']
    list_filter = ['status', 'sale_timestamp', 'employee']
    search_fields = ['id', 'employee__username']
    readonly_fields = ['sale_timestamp', 'created_at']
    inlines = [SaleItemInline]
    
    fieldsets = (
        ('Sale Information', {
            'fields': ('employee', 'status')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax', 'discount_applied', 'total')
        }),
        ('Timestamps', {
            'fields': ('sale_timestamp', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'item', 'quantity', 'unit_price', 'line_total']
    list_filter = ['created_at']
    search_fields = ['item__name', 'sale__id']
    readonly_fields = ['line_total', 'created_at']
