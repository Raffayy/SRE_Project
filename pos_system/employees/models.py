"""
Employee models for POS System
Learn: This shows how to create Django models with validation
"""
from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.hashers import make_password, check_password


class Employee(models.Model):
    """
    Employee model - represents system users
    
    Learn: 
    - CharField for text fields
    - choices parameter for restricted values
    - unique=True prevents duplicates
    - auto_now_add sets timestamp on creation
    """
    
    POSITION_CHOICES = [
        ('Admin', 'Admin'),
        ('Cashier', 'Cashier'),
    ]
    
    username = models.CharField(
        max_length=50,
        unique=True,
        validators=[MinLengthValidator(3)],
        help_text="Unique username for login"
    )
    
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Full name of employee"
    )
    
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        help_text="Employee role: Admin or Cashier"
    )
    
    password_hash = models.CharField(
        max_length=255,
        help_text="Hashed password (never store plain text!)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When employee was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When employee was last updated"
    )
    
    class Meta:
        db_table = 'employees'
        ordering = ['username']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
    
    def __str__(self):
        return f"{self.username} ({self.position})"
    
    def set_password(self, raw_password):
        """
        Hash and set password
        Learn: Always hash passwords, never store plain text!
        """
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        """
        Verify password against hash
        Learn: Use Django's built-in password checking
        """
        return check_password(raw_password, self.password_hash)
    
    def is_admin(self):
        """Check if employee is admin"""
        return self.position == 'Admin'
    
    def can_manage_employees(self):
        """Check if employee can manage other employees"""
        return self.is_admin()


class EmployeeActivityLog(models.Model):
    """
    Log of employee activities for audit trail
    
    Validates: Requirements 6.4
    """
    
    ACTION_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('SALE', 'Sale Transaction'),
        ('RENTAL', 'Rental Transaction'),
        ('RETURN', 'Return Transaction'),
        ('EMPLOYEE_CREATE', 'Employee Created'),
        ('EMPLOYEE_UPDATE', 'Employee Updated'),
        ('EMPLOYEE_DELETE', 'Employee Deleted'),
        ('INVENTORY_UPDATE', 'Inventory Updated'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )
    
    details = models.TextField(
        blank=True,
        help_text="Additional details about the action"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action occurred"
    )
    
    class Meta:
        db_table = 'employee_activity_log'
        ordering = ['-timestamp']
        verbose_name = 'Employee Activity Log'
        verbose_name_plural = 'Employee Activity Logs'
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['employee', '-timestamp']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.employee.username} - {self.action} at {self.timestamp}"
