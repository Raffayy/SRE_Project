from typing import Optional
import bcrypt
from .models import Employee
from .repositories import IEmployeeRepository

class AuthenticationService:
    """Handles user authentication"""
    
    def __init__(self, employee_repository: IEmployeeRepository):
        self.employee_repository = employee_repository
    
    def authenticate(self, username: str, password: str) -> Optional[Employee]:
        """Authenticate user and return employee if valid"""
        employee = self.employee_repository.find_by_username(username)
        
        if employee is None:
            return None
            
        # In a real app with hashed passwords, we would use bcrypt.checkpw
        # For this reengineering, we assume passwords might be migrated as plain text or hashed
        # Checking if the model has a check_password method (Django AbstractBaseUser)
        if hasattr(employee, 'check_password'):
             if employee.check_password(password):
                 return employee
        
        # Fallback for plain text or custom hash if not using Django auth fully yet
        if employee.password == password:
            return employee
            
        return None
        
    def hash_password(self, plain_password: str) -> str:
        """Hash a password for storage"""
        # Example using bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')

class AuditLogger:
    """Handles audit trail logging"""
    
    def log_login(self, username: str, success: bool, reason: str = None):
        from .models import EmployeeActivityLog, Employee
        
        employee = Employee.objects.filter(username=username).first()
        if employee:
            action = 'LOGIN_SUCCESS' if success else 'LOGIN_FAILED'
            details = reason if reason else "Login successful"
            
            EmployeeActivityLog.objects.create(
                employee=employee,
                action=action,
                details=details
            )
        else:
            # Log failed attempt for unknown user? 
            # For now just print as we need an employee object for the FK
            print(f"AUDIT: Login attempt for unknown user {username} - Success: {success}")
        
    def log_transaction(self, employee_name: str, transaction_type: str, amount: str):
        from .models import EmployeeActivityLog, Employee
        
        employee = Employee.objects.filter(name=employee_name).first()
        if employee:
            EmployeeActivityLog.objects.create(
                employee=employee,
                action='TRANSACTION',
                details=f"{transaction_type} for ${amount}"
            )

