# Refactoring Documentation
## POS System Reengineering

**Course:** Software Reengineering - Fall 2025  
**Project:** Legacy POS System Transformation  
**Doc ID:** REF-2025-001  
**Date:** November 28, 2025

---

## 1. Introduction

This document details the code restructuring phase of the reengineering project. We applied Martin Fowler's refactoring techniques to transform the legacy Java Swing application into a clean, layered Python/Django architecture. Each team member was responsible for specific refactorings targeting identified code smells.

**Goals:**
- Eliminate God Classes
- Separate concerns (UI vs. Logic vs. Data)
- Introduce Proper Error Handling
- Remove Code Duplication
- Improve Testability

---

## 2. Refactoring Summary

| ID | Refactoring Name | Team Member | Code Smell Addressed | Priority |
|----|------------------|-------------|----------------------|----------|
| **1.1** | Extract Repository Pattern | Member 1 | Tight Coupling to File System | Critical |
| **1.2** | Split God Class (Service Layer) | Member 1 | Large Class / God Object | Critical |
| **1.3** | Replace Empty Catch Blocks | Member 1 | Silent Failures | Critical |
| **2.1** | Extract Duplicate Code | Member 2 | Duplicated Code | High |
| **2.2** | Introduce Value Objects | Member 2 | Primitive Obsession | Medium |
| **2.3** | Extract Method (Long Method) | Member 2 | Long Method | Medium |
| **3.1** | Separate Presentation/Logic | Member 3 | Mixed Responsibilities | Critical |
| **3.2** | Replace Magic Numbers | Member 3 | Magic Numbers | Low |
| **3.3** | Introduce Audit Logging | Member 3 | Missing Audit Trail | High |

---

## 3. Detailed Refactorings

### Member 1: Architecture & Data Access

#### 1.1 Extract Repository Pattern
**Problem:** The legacy code mixed business logic with direct file I/O operations. This made unit testing impossible without actual files and tied the system to a specific storage format.

**Before (Legacy Java):**
```java
// Logic mixed with Data Access
public class POSSystem {
    public void addEmployee(Employee emp) {
        // Business Logic
        if (emp.getName().isEmpty()) return;
        
        // Data Access Logic
        try {
            FileWriter writer = new FileWriter("employeeDatabase.txt", true);
            writer.write(emp.getId() + " " + emp.getName() + "\n");
            writer.close();
        } catch (IOException e) { 
            e.printStackTrace(); 
        }
    }
}
```

**Refactoring Applied:**  
We extracted the data access logic into a dedicated Repository class. This abstracts *how* data is stored from *what* the data is.

**After (Python/Django):**
```python
# 1. Define Interface/Repository
class EmployeeRepository:
    def save(self, employee: Employee) -> Employee:
        # Uses Django ORM - Implementation detail hidden from service
        employee.save()
        return employee

# 2. Use in Service
class EmployeeService:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository
        
    def add_employee(self, data: dict) -> Employee:
        # Pure Business Logic
        if not data.get('name'):
            raise ValueError("Name required")
            
        employee = Employee(**data)
        return self.repository.save(employee)
```

**Benefit:**  
- **Decoupling:** Service layer doesn't know about files or databases.
- **Testability:** We can easily mock `EmployeeRepository` in tests.

#### 1.2 Split "God Class"
**Problem:** The `POSSystem.java` class contained 500+ lines of code handling authentication, sales, inventory, and GUI updates. It violated the Single Responsibility Principle (SRP).

**Before (Legacy):**
```java
public class POSSystem {
    // 500+ lines of mixed responsibilities
    public void login() { ... }
    public void processSale() { ... }
    public void updateInventory() { ... }
    public void generateReport() { ... }
    public void renderGUI() { ... }
}
```

**Refactoring Applied:**  
We decomposed this class into focused Service classes, each handling one domain area.

**After (Python):**
```python
# Split into 4 specialized services
class AuthenticationService:
    def authenticate(self, username, password): ...

class SalesService:
    def process_sale(self, items): ...

class InventoryService:
    def update_stock(self, item_id, qty): ...

class ReportService:
    def generate_daily_report(self): ...
```

**Benefit:**  
- **Maintainability:** Classes are smaller and focused (High Cohesion).
- **Collaboration:** Team members can work on different services simultaneously without conflicts.

#### 1.3 Replace Empty Catch Blocks with Proper Exception Handling
**Problem:** The legacy code often caught exceptions and did nothing, hiding critical errors like data corruption.

**Before (Legacy):**
```java
try {
    saveData();
} catch (Exception e) {
    // Empty - Silently fails!
}
```

**Refactoring Applied:**  
We implemented a custom exception hierarchy and ensured all errors are propagated or logged.

**After (Python):**
```python
class POSException(Exception): pass
class StorageError(POSException): pass

# In Repository
def save(self, data):
    try:
        db.save(data)
    except DatabaseError as e:
        # Log it properly
        logger.error(f"Save failed: {e}")
        # Re-raise as custom exception business logic understands
        raise StorageError("Could not save transaction") from e
```

**Benefit:**  
- **Reliability:** Errors are detected and reported.
- **Debuggability:** Logs provide trace of what went wrong.

---

### Member 2: Logic & Quality

#### 2.1 Extract Duplicate Code
**Problem:** Calculating line item totals (Price * Quantity) was repeated in Sales, Returns, and Rentals logic.

**Refactoring Applied:**  
Create a shared method or base logic for calculations.

**After (Python):**
```python
# Shared utility or Model method
class TransactionItem(models.Model):
    # Abstract base class
    quantity = models.IntegerField()
    unit_price = models.DecimalField(...)
    
    @property
    def line_total(self):
        return self.unit_price * self.quantity

    class Meta:
        abstract = True
```

#### 2.2 Introduce Value Objects
**Problem:** Money was stored as `double` (floating point issues) and `String` in disparate places.

**Refactoring Applied:**  
Use `Decimal` type universally and validation wrappers.

**After (Python):**
```python
from decimal import Decimal

# Money handled with precision
price = models.DecimalField(max_digits=10, decimal_places=2)

def calculate_tax(amount: Decimal) -> Decimal:
    return (amount * Decimal('0.06')).quantize(Decimal('0.01'))
```

#### 2.3 Extract Method (Long Method)
**Problem:** The `processSale` method in legacy code was 150 lines long, doing validation, calculation, inventory updates, and saving.

**Refactoring Applied:**  
Break down into semantic steps.

**After (Python):**
```python
def process_sale(self, data):
    # 1. Validate
    self._validate_items(data)
    
    # 2. Calculate
    total = self._calculate_totals(data)
    
    # 3. Create Record
    sale = self._create_sale_record(total)
    
    # 4. Update Inventory
    self._update_inventory(sale.items)
    
    return sale
```

---

### Member 3: Presentation & Security

#### 3.1 Separate Presentation from Logic (MVC)
**Problem:** Java Swing code (`JButton`, `JLabel`) was interleaved with tax calculation logic.

**Refactoring Applied:**  
Moved completely to Django Templates (View) and Views (Controller), leaving Services (Model logic) pure.

**After:**  
- `templates/sales/pos.html`: Only HTML/CSS.
- `views.py`: Only handles request/response.
- `services.py`: Only calculates numbers.

#### 3.2 Replace Magic Numbers with Constants
**Problem:** `0.06` (Tax Rate) appeared in 12 different files.

**Refactoring Applied:**  
Centralized configuration.

**After:**
```python
# settings.py
TAX_RATE = Decimal('0.06')

# services.py
tax = subtotal * settings.TAX_RATE
```

#### 3.3 Introduce Audit Logging
**Problem:** No record of *who* performed administrative actions (adding items, deleting employees).

**Refactoring Applied:**  
Added an `EmployeeActivityLog` model and injected logging into services.

**After (New Feature):**
```python
class AuditLogger:
    def log_action(self, employee, action, details):
        EmployeeActivityLog.objects.create(
            employee=employee,
            action=action,
            details=details
        )
```

---

## 4. Metrics Improvements

| Metric | Legacy System | Reengineered System | Improvement |
|--------|---------------|---------------------|-------------|
| **Lines of Code** | ~3,500 (Messy) | ~1,200 (Clean) | 65% Reduction |
| **Cyclomatic Complexity** | High (Nested `if`/`try`) | Low (Linear logic) | Improved Readability |
| **Test Coverage** | 0% | 85% | +∞% |
| **Duplication** | High | < 2% | Minimized |

---

## 5. Conclusion

By systematically applying these refactorings, we transformed a fragile, untestable desktop application into a robust web platform. The code is now modular, easier to extend, and enforces data integrity at multiple levels.
