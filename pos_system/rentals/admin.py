from django.contrib import admin
from .models import Rental, RentalItem


class RentalItemInline(admin.TabularInline):
    model = RentalItem
    extra = 1
    readonly_fields = ['line_total']


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_phone', 'employee', 'rental_timestamp', 'due_date', 'total', 'status', 'is_overdue']
    list_filter = ['status', 'rental_timestamp', 'due_date']
    search_fields = ['id', 'customer_phone', 'employee__username']
    readonly_fields = ['rental_timestamp', 'created_at']
    inlines = [RentalItemInline]
    
    fieldsets = (
        ('Rental Information', {
            'fields': ('employee', 'customer_phone', 'status')
        }),
        ('Dates', {
            'fields': ('rental_timestamp', 'due_date')
        }),
        ('Amount', {
            'fields': ('total',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(RentalItem)
class RentalItemAdmin(admin.ModelAdmin):
    list_display = ['rental', 'item', 'quantity', 'unit_price', 'line_total']
    list_filter = ['created_at']
    search_fields = ['item__name', 'rental__id', 'rental__customer_phone']
    readonly_fields = ['line_total', 'created_at']
