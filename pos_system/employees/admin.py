from django.contrib import admin
from .models import Employee, EmployeeActivityLog


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'position', 'created_at']
    list_filter = ['position', 'created_at']
    search_fields = ['username', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('username', 'name', 'position')
        }),
        ('Security', {
            'fields': ('password_hash',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmployeeActivityLog)
class EmployeeActivityLogAdmin(admin.ModelAdmin):
    list_display = ['employee', 'action', 'timestamp', 'details']
    list_filter = ['action', 'timestamp', 'employee']
    search_fields = ['employee__username', 'details']
    readonly_fields = ['timestamp']
    
    def has_add_permission(self, request):
        # Logs should be created automatically, not manually
        return False
    
    def has_change_permission(self, request, obj=None):
        # Logs should not be modified
        return False
