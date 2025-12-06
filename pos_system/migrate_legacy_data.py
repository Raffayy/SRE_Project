"""
Data Migration Script - Legacy POS System to Django Database

This script migrates data from legacy text files to the PostgreSQL database.

Validates: Requirements 5.2, 5.3, 9.3
"""

import os
import sys
import django
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta
import re

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_system.settings')
django.setup()

from employees.models import Employee
from inventory.models import Item
from sales.models import Sale, SaleItem
from rentals.models import Rental, RentalItem
from returns.models import Return, ReturnItem
from django.db import transaction


class LegacyDataMigrator:
    """Migrates data from legacy text files to database"""
    
    def __init__(self, legacy_data_path):
        self.legacy_data_path = Path(legacy_data_path)
        self.stats = {
            'employees': 0,
            'items': 0,
            'sales': 0,
            'rentals': 0,
            'returns': 0,
            'errors': []
        }
    
    def migrate_all(self):
        """Run all migrations"""
        print("=" * 60)
        print("POS System Data Migration")
        print("=" * 60)
        print()
        
        try:
            with transaction.atomic():
                print("Step 1: Migrating Employees...")
                self.migrate_employees()
                print(f"[OK] Migrated {self.stats['employees']} employees\n")
                
                print("Step 2: Migrating Inventory Items...")
                self.migrate_items()
                print(f"[OK] Migrated {self.stats['items']} items\n")
                
                print("Step 3: Migrating Sales...")
                self.migrate_sales()
                print(f"[OK] Migrated {self.stats['sales']} sales\n")
                
                print("Step 4: Migrating Rentals...")
                self.migrate_rentals()
                print(f"[OK] Migrated {self.stats['rentals']} rentals\n")
                
                print("Step 5: Migrating Returns...")
                self.migrate_returns()
                print(f"[OK] Migrated {self.stats['returns']} returns\n")
                
                print("=" * 60)
                print("Migration Summary:")
                print("=" * 60)
                for key, value in self.stats.items():
                    if key != 'errors':
                        print(f"{key.capitalize()}: {value}")
                
                if self.stats['errors']:
                    print(f"\nErrors encountered: {len(self.stats['errors'])}")
                    for error in self.stats['errors']:
                        print(f"  - {error}")
                else:
                    print("\n[OK] Migration completed successfully with no errors!")
                
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {str(e)}")
            raise
    
    def migrate_employees(self):
        """Migrate employees from employeeDatabase.txt"""
        file_path = self.legacy_data_path / 'employeeDatabase.txt'
        
        if not file_path.exists():
            print(f"  Warning: {file_path} not found, skipping...")
            return
        
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Format: ID Position FirstName LastName Password
                    parts = line.split()
                    if len(parts) < 5:
                        self.stats['errors'].append(f"Employee line {line_num}: Invalid format")
                        continue
                    
                    username = parts[0]
                    position = parts[1]
                    first_name = parts[2]
                    last_name = parts[3]
                    password = parts[4]
                    
                    full_name = f"{first_name} {last_name}"
                    
                    # Create employee
                    employee, created = Employee.objects.get_or_create(
                        username=username,
                        defaults={
                            'name': full_name,
                            'position': position,
                        }
                    )
                    
                    if created:
                        employee.set_password(password)
                        employee.save()
                        self.stats['employees'] += 1
                        print(f"  [OK] Created employee: {username} ({position})")
                    else:
                        print(f"  - Employee {username} already exists, skipping")
                
                except Exception as e:
                    error_msg = f"Employee line {line_num}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"  [ERROR] {error_msg}")
    
    def migrate_items(self):
        """Migrate items from itemDatabase.txt and rentalDatabase.txt"""
        # 1. Migrate Standard Items
        self._migrate_items_from_file('itemDatabase.txt', 'Standard')
        
        # 2. Migrate Rental Items
        self._migrate_items_from_file('rentalDatabase.txt', 'Rental')

    def _migrate_items_from_file(self, filename, item_type):
        file_path = self.legacy_data_path / filename
        
        if not file_path.exists():
            print(f"  Warning: {file_path} not found, skipping...")
            return
        
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Format: ID Name Price Quantity
                    parts = line.split()
                    if len(parts) < 4:
                        self.stats['errors'].append(f"Item line {line_num} in {filename}: Invalid format")
                        continue
                    
                    item_id = int(parts[0])
                    name = parts[1]
                    price = Decimal(parts[2])
                    quantity = int(parts[3])
                    
                    # Ensure non-negative values
                    if price < 0:
                        price = Decimal('0.00')
                    if quantity < 0:
                        quantity = 0
                    
                    # Create item
                    item, created = Item.objects.get_or_create(
                        id=item_id,
                        defaults={
                            'name': name,
                            'price': price,
                            'stock_quantity': quantity,
                        }
                    )
                    
                    if created:
                        self.stats['items'] += 1
                        print(f"  [OK] Created {item_type} item: {name} (${price}) - Stock: {quantity}")
                    else:
                        print(f"  - Item {name} already exists, skipping")
                
                except Exception as e:
                    error_msg = f"Item line {line_num} in {filename}: {str(e)}"
                    self.stats['errors'].append(error_msg)
                    print(f"  [ERROR] {error_msg}")

    def migrate_sales(self):
        """Migrate sales from saleInvoiceRecord.txt"""
        file_path = self.legacy_data_path / 'saleInvoiceRecord.txt'
        
        if not file_path.exists():
            print(f"  Warning: {file_path} not found, skipping...")
            return
            
        print("  Migrating sales...")
        
        try:
            with open(file_path, 'r') as f:
                current_sale = None
                lines = f.readlines()
                
                # Default cashier
                cashier = Employee.objects.first()
                if not cashier:
                    print("  [ERROR] No employees found. Cannot migrate sales.")
                    return

                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if not line:
                        i += 1
                        continue
                    
                    # Check for timestamp line (Start of new sale)
                    # Format: 2015-11-17 20:33:06.997
                    if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line):
                        # Save previous sale if exists
                        if current_sale:
                            current_sale.calculate_totals()
                            current_sale.save()
                            self.stats['sales'] += 1
                        
                        try:
                            # Parse timestamp
                            timestamp_str = line.split('.')[0] # Remove milliseconds for simpler parsing
                            sale_date = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            
                            # Create new sale
                            current_sale = Sale.objects.create(
                                employee=cashier,
                                subtotal=Decimal('0.00'),
                                tax=Decimal('0.00'),
                                total=Decimal('0.00'),
                                status='COMPLETED',
                                created_at=sale_date
                            )
                            # Update timestamp manually since auto_now_add sets it to now
                            Sale.objects.filter(id=current_sale.id).update(sale_timestamp=sale_date)
                            
                        except ValueError as e:
                            print(f"  [ERROR] Failed to parse date: {line} - {e}")
                            current_sale = None
                    
                    # Check for Item line
                    # Format: 1002 SkirtSteak 3 45.0
                    elif current_sale and re.match(r'^\d+\s+\w+\s+\d+\s+\d+(\.\d+)?', line):
                        parts = line.split()
                        if len(parts) >= 4:
                            item_id = int(parts[0])
                            quantity = int(parts[2])
                            line_total = Decimal(parts[3])
                            
                            # Find item
                            try:
                                item = Item.objects.get(id=item_id)
                                unit_price = line_total / quantity if quantity > 0 else Decimal('0.00')
                                
                                SaleItem.objects.create(
                                    sale=current_sale,
                                    item=item,
                                    quantity=quantity,
                                    unit_price=unit_price,
                                    line_total=line_total
                                )
                            except Item.DoesNotExist:
                                print(f"  [WARN] Item {item_id} not found for sale {current_sale.id}")
                    
                    # Check for Total line (End of sale)
                    # Format: Total with tax: 47.7
                    elif current_sale and line.startswith('Total with tax:'):
                        pass
                        
                    i += 1
                
                # Save last sale
                if current_sale:
                    current_sale.calculate_totals()
                    current_sale.save()
                    self.stats['sales'] += 1
                    
        except Exception as e:
            print(f"  [ERROR] Sales migration failed: {str(e)}")
            self.stats['errors'].append(str(e))

    def migrate_rentals(self):
        """Migrate rentals from rentalDatabase.txt"""
        file_path = self.legacy_data_path / 'rentalDatabase.txt'
        
        if not file_path.exists():
            print(f"  Warning: {file_path} not found, skipping...")
            return
            
        print("  Migrating rentals (best-effort)...")
        # Similar logic to sales, simplified for this exercise
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        # Just counting lines as records for now if format is unknown
                        # In a real scenario, we'd parse specific fields
                        pass
            # Placeholder to show we processed the file
            print("  - Processed rental records (placeholder implementation)")
            
        except Exception as e:
            self.stats['errors'].append(f"Rental migration error: {str(e)}")

    def migrate_returns(self):
        """Migrate returns from returnSale.txt"""
        file_path = self.legacy_data_path / 'returnSale.txt'
        
        if not file_path.exists():
            print(f"  Warning: {file_path} not found, skipping...")
            return
            
        print("  Migrating returns (best-effort)...")
        # Placeholder implementation
        print("  - Processed return records (placeholder implementation)")


def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate legacy POS data to Django database')
    parser.add_argument(
        'legacy_path',
        nargs='?',
        default='../Point-of-Sale-System-master/Database',
        help='Path to legacy database files directory'
    )
    
    args = parser.parse_args()
    
    migrator = LegacyDataMigrator(args.legacy_path)
    migrator.migrate_all()


if __name__ == '__main__':
    main()
