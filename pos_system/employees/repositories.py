from abc import ABC, abstractmethod
from typing import Optional
from .models import Employee

class IEmployeeRepository(ABC):
    """Repository interface for Employee data access"""
    
    @abstractmethod
    def find_by_username(self, username: str) -> Optional[Employee]:
        """Find employee by username"""
        pass
    
    @abstractmethod
    def save(self, employee: Employee) -> Employee:
        """Save employee"""
        pass

class EmployeeRepository(IEmployeeRepository):
    """Concrete implementation using Django ORM"""
    
    def find_by_username(self, username: str) -> Optional[Employee]:
        try:
            return Employee.objects.get(username=username)
        except Employee.DoesNotExist:
            return None
            
    def save(self, employee: Employee) -> Employee:
        employee.save()
        return employee
