# Database Setup Guide
## POS System Reengineering

**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

---

## Prerequisites

1. **PostgreSQL 15+** installed
2. **Python 3.11+** installed
3. **Virtual environment** activated

---

## Step 1: Install PostgreSQL

### Windows
```powershell
# Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey
choco install postgresql

# Start PostgreSQL service
net start postgresql-x64-15
```

### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Mac
brew install postgresql@15
brew services start postgresql@15
```

---

## Step 2: Create Database and User

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE pos_system;

-- Create user (optional, or use postgres user)
CREATE USER pos_admin WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE pos_system TO pos_admin;

-- Exit
\q
```

---

## Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your database credentials
# Update these values:
DB_NAME=pos_system
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
```

---

## Step 4: Install Python Dependencies

```bash
# Activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 5: Run Database Migrations

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# You should see output like:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, employees, inventory, rentals, returns, sales, sessions
# Running migrations:
#   Applying employees.0001_initial... OK
#   Applying inventory.0001_initial... OK
#   Applying sales.0001_initial... OK
#   Applying rentals.0001_initial... OK
#   Applying returns.0001_initial... OK
```

---

## Step 6: Verify Database Schema

```bash
# Connect to database
psql -U postgres -d pos_system

# List all tables
\dt

# You should see:
# employees
# employee_activity_log
# items
# inventory_adjustments
# sales
# sale_items
# rentals
# rental_items
# returns
# return_items

# Describe a table
\d employees

# Exit
\q
```

---

## Step 7: Create Superuser

```bash
# Create Django admin superuser
python manage.py createsuperuser

# Follow prompts:
# Username: admin
# Email: admin@example.com
# Password: ********
```

---

## Step 8: Migrate Legacy Data

```bash
# Run migration script
python migrate_legacy_data.py ../Point-of-Sale-System-master/Database

# This will:
# - Migrate employees from employeeDatabase.txt
# - Migrate items from itemDatabase.txt
# - Migrate sales from saleInvoiceRecord.txt
# - Migrate rentals from rentalDatabase.txt
# - Migrate returns from returnSale.txt
```

---

## Step 9: Verify Data Migration

```bash
# Start Django shell
python manage.py shell

# Check migrated data
>>> from employees.models import Employee
>>> Employee.objects.count()
12  # Should match number of employees in legacy system

>>> from inventory.models import Item
>>> Item.objects.count()
101  # Should match number of items in legacy system

>>> # List all employees
>>> for emp in Employee.objects.all():
...     print(f"{emp.username} - {emp.position}")

>>> exit()
```

---

## Step 10: Start Development Server

```bash
# Run server
python manage.py runserver

# Access application
# - Main site: http://localhost:8000
# - Admin interface: http://localhost:8000/admin
```

---

## Database Schema

### Entity-Relationship Diagram

```
┌─────────────┐
│  employees  │
└──────┬──────┘
       │
       │ (1:N)
       │
       ├──────────────────┬──────────────────┬──────────────────┐
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    sales    │    │   rentals   │    │   returns   │    │  activity   │
│             │    │             │    │             │    │     log     │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └─────────────┘
       │                  │                  │
       │ (1:N)            │ (1:N)            │ (1:N)
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ sale_items  │    │rental_items │    │return_items │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       │ (N:1)            │ (N:1)            │ (N:1)
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │    items    │
                   └─────────────┘
```

### Tables

**employees**
- id (PK)
- username (UNIQUE)
- name
- position (Admin/Cashier)
- password_hash
- created_at
- updated_at

**items**
- id (PK)
- name
- price (DECIMAL, >= 0)
- stock_quantity (INTEGER, >= 0)
- created_at
- updated_at

**sales**
- id (PK)
- employee_id (FK → employees)
- sale_timestamp
- subtotal
- tax
- total
- discount_applied
- status
- created_at

**sale_items**
- id (PK)
- sale_id (FK → sales)
- item_id (FK → items)
- quantity
- unit_price
- line_total
- created_at

**rentals**
- id (PK)
- employee_id (FK → employees)
- customer_phone
- rental_timestamp
- due_date
- total
- status
- created_at

**rental_items**
- id (PK)
- rental_id (FK → rentals)
- item_id (FK → items)
- quantity
- unit_price
- line_total
- created_at

**returns**
- id (PK)
- original_sale_id (FK → sales, nullable)
- original_rental_id (FK → rentals, nullable)
- employee_id (FK → employees)
- return_timestamp
- refund_amount
- late_fee
- reason
- created_at

**return_items**
- id (PK)
- return_transaction_id (FK → returns)
- item_id (FK → items)
- quantity
- unit_price
- line_total
- created_at

**employee_activity_log**
- id (PK)
- employee_id (FK → employees)
- action
- details
- timestamp

**inventory_adjustments**
- id (PK)
- item_id (FK → items)
- adjustment_type
- quantity_change
- previous_quantity
- new_quantity
- reason
- adjusted_by (FK → employees)
- adjusted_at

---

## Troubleshooting

### Issue: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### Issue: "Connection refused"
```bash
# Check if PostgreSQL is running
# Windows:
net start postgresql-x64-15

# Linux/Mac:
sudo service postgresql start
```

### Issue: "Database does not exist"
```sql
-- Connect and create database
psql -U postgres
CREATE DATABASE pos_system;
\q
```

### Issue: "Permission denied"
```sql
-- Grant permissions
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE pos_system TO your_user;
\q
```

---

## Data Integrity Validation

After migration, verify data integrity:

```bash
# Run validation script
python manage.py shell

>>> from django.db import connection
>>> cursor = connection.cursor()

>>> # Check foreign key constraints
>>> cursor.execute("""
...     SELECT COUNT(*) FROM sales s
...     LEFT JOIN employees e ON s.employee_id = e.id
...     WHERE e.id IS NULL
... """)
>>> cursor.fetchone()[0]  # Should be 0

>>> # Check for negative prices
>>> from inventory.models import Item
>>> Item.objects.filter(price__lt=0).count()  # Should be 0

>>> # Check for negative stock
>>> Item.objects.filter(stock_quantity__lt=0).count()  # Should be 0
```

---

## Backup and Restore

### Backup
```bash
# Backup database
pg_dump -U postgres pos_system > pos_system_backup.sql

# Backup with timestamp
pg_dump -U postgres pos_system > pos_system_$(date +%Y%m%d_%H%M%S).sql
```

### Restore
```bash
# Restore database
psql -U postgres pos_system < pos_system_backup.sql
```

---

**Document Version:** 1.0  
**Last Updated:** November 28, 2025  
**Status:** Database Setup Complete ✓
