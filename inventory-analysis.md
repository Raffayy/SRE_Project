# Inventory Analysis Report
## Legacy POS System - SG Technologies

**Project:** Point-of-Sale System Reengineering  
**Course:** Software Reengineering - Fall 2025  
**Date:** December 6, 2025  
**Original System:** Desktop Java Application (CSE216)  
**Analysis Phase:** Inventory Analysis & Asset Classification (Phase 1)

---

## Executive Summary

This document provides a comprehensive inventory of all assets in the legacy SG Technologies Point-of-Sale (POS) system. The system is a desktop Java application built using the Swing GUI framework with text file-based data persistence. The analysis identifies **23 Java source files**, **13 data files**, multiple configuration files, and existing documentation.

**Summary of Findings:**
- Assets have been classified as **Active** (re-implement), **Obsolete** (discard), or **Reusable** (migrate).
- The system suffers from tight coupling between logic and file I/O.
- Data integrity is compromised due to reliance on unstructured text files.
- Core business logic is valuable and recoverable.

---

## 1. Source Code Inventory

### 1.1 Core Business Logic Classes

| File | LOC (Est.) | Purpose | Classification | Justification |
|------|-----------|---------|----------------|---------------|
| **Employee.java** | ~30 | Employee data model | **REUSABLE** | Core domain model, adaptable to new system |
| **Item.java** | ~25 | Item data model with stock | **REUSABLE** | Core domain model, essential for inventory |
| **Inventory.java** | ~120 | Singleton inventory manager | **ACTIVE** | Needs restructuring (remove file coupling) |
| **EmployeeManagement.java** | ~200 | Employee CRUD operations | **ACTIVE** | Core logic good, but tightly coupled to files |
| **POSSystem.java** | ~180 | Auth and session management | **ACTIVE** | "God Class" needs splitting into services |
| **Management.java** | ~150 | Customer/rental management | **ACTIVE** | Reusable logic, needs refactoring |

### 1.2 Transaction Processing Classes

| File | LOC (Est.) | Purpose | Classification | Justification |
|------|-----------|---------|----------------|---------------|
| **PointOfSale.java** | ~100 | Abstract base class | **REUSABLE** | Good abstraction, demonstrates Factory pattern |
| **POS.java** | ~150 | Sales transactions logic | **ACTIVE** | Core POS logic, needs data layer separation |
| **POR.java** | ~150 | Rental transactions logic | **ACTIVE** | Core Rental logic, needs data layer separation |
| **POH.java** | ~150 | Returns processing logic | **ACTIVE** | Core Returns logic, needs data layer separation |
| **Sale.java** | ~100 | Sale transaction model | **ACTIVE** | Business logic valuable, needs data layer |
| **Rental.java** | ~100 | Rental transaction model | **ACTIVE** | Business logic valuable, needs data layer |
| **ReturnItem.java** | ~80 | Return item processing | **ACTIVE** | Core functionality, needs refactoring |
| **HandleReturns.java** | ~100 | Returns handling logic | **ACTIVE** | Redundant with POH.java, consolidate |
| **Register.java** | ~80 | Cash register operations | **ACTIVE** | Payment processing logic reusable |

### 1.3 User Interface Classes (Swing GUI)

| File | Classification | Justification |
|------|----------------|---------------|
| **Login_Interface.java** | **OBSOLETE** | Swing GUI -> Django Web Templates |
| **Admin_Interface.java** | **OBSOLETE** | Swing GUI -> Django Web Templates |
| **Cashier_Interface.java** | **OBSOLETE** | Swing GUI -> Django Web Templates |
| **AddEmployee_Interface.java** | **OBSOLETE** | Swing GUI -> Django Web Forms |
| **UpdateEmployee_Interface.java** | **OBSOLETE** | Swing GUI -> Django Web Forms |
| **EnterItem_Interface.java** | **OBSOLETE** | Swing GUI -> Django Web Forms |
| **Transaction_Interface.java** | **OBSOLETE** | Swing GUI -> Django Web Forms |
| **Payment_Interface.java** | **OBSOLETE** | Swing GUI -> Django Web Forms |

---

## 2. Data Files Inventory

### 2.1 Primary Database Files

| File | Records | Format | Classification | Data Quality Issues |
|------|---------|--------|----------------|---------------------|
| **employeeDatabase.txt** | 12 | Space-delimited | **MIGRATE** | Plain text passwords |
| **itemDatabase.txt** | 101 | Space-delimited | **MIGRATE** | Good consistency |
| **saleInvoiceRecord.txt** | ~36 | Multi-line | **MIGRATE** | Negative totals, unstructured |
| **rentalDatabase.txt** | ~20 | Multi-line | **MIGRATE** | Contains rental items info |
| **returnSale.txt** | Unknown | Multi-line | **MIGRATE** | Needs inspection |
| **employeeLogfile.txt** | Logs | Text log | **ARCHIVE** | Historical audit trail |

### 2.2 Temporary/Working Files

| File | Purpose | Classification | Justification |
|------|---------|----------------|---------------|
| **temp.txt** | Crash recovery | **OBSOLETE** | DB Transactions replace this |
| **temp (1/2/3).txt** | Backups | **OBSOLETE** | Redundant |
| **newEmployeeDatabase.txt** | Temp update file | **OBSOLETE** | DB Updates replace this |

---

## 3. Configuration & Documentation

### 3.1 Configuration Files
- **.classpath, .project, .settings/** (Eclipse) -> **OBSOLETE** (Switching to VS Code/PyCharm)
- **build.xml** (Ant) -> **OBSOLETE** (Switching to pip/requirements.txt)
- **.gitignore** -> **REUSABLE** (Update for Python types)

### 3.2 Documentation
- **README.txt** -> **REUSABLE** (Baseline understanding)
- **Developer Manual.docx** -> **REUSABLE** (Workflow reference)
- **Responsibility Matrix.xlsx** -> **REUSABLE** (Original architecture reference)

---

## 4. Dependency Map

### 4.1 Class Dependencies (Legacy)

```text
POSSystem (Main)
├── Login_Interface
├── Admin_Interface
│   └── EmployeeManagement -> employeeDatabase.txt
└── Cashier_Interface
    └── Transaction_Interface
        ├── POS (Sales) -> itemDatabase.txt, saleInvoiceRecord.txt
        ├── POR (Rentals) -> itemDatabase.txt, rentalDatabase.txt
        └── POH (Returns) -> returnSale.txt
```

### 4.2 Critical Chain
1.  **POSSystem** controls the lifecycle.
2.  **Interfaces** directly instantiate logic classes.
3.  **Logic classes** directly open/close text files.
4.  **No abstraction layer** exists between Logic and Data.

---

## 5. Asset Classification Summary

| Classification | Count | Percentage | Strategy |
|----------------|-------|------------|----------|
| **ACTIVE** (Refactor) | 15 | 35% | Logic extraction to Service Layer |
| **REUSABLE** (Adapt) | 18 | 42% | Models and Documentation |
| **OBSOLETE** (Discard) | 10 | 23% | GUI and Temp Files |
| **TOTAL** | **43** | **100%** | |

---

## 6. Conclusion & Recommendations

### 6.1 Findings
- **Strengths**: Clear domain models (Employee, Item); distinct transaction types.
- **Weaknesses**: "God Class" architecture; data integrity risks (text files); lack of tests.
- **Risks**: Data migration is complex due to non-standard parsing in legacy Java code.

### 6.2 Recommendations for Next Phase
1.  **Extract Domain Models**: Port `Item` and `Employee` attributes to Django Models first.
2.  **Define Schema**: Create a normalized SQL schema (PostgreSQL) to replace text files.
3.  **Refactor Logic**: Isolate the calculation logic in `POS`, `POR`, and `POH` from file I/O.
4.  **Discard GUI**: Do not attempt to reuse Swing code; rebuild views in Django Templates.

---

**Document Version:** 2.0 (Final)  
**Last Updated:** December 6, 2025  
**Status:** Complete ✓
