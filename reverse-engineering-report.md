# Reverse Engineering Report

## 1. Introduction
This report documents the reverse engineering process of the legacy SG Technologies Point-of-Sale (POS) system. The goal was to recover the design, architecture, and business logic from the existing source code and artifacts to facilitate the reengineering process.

## 2. Methodology
The reverse engineering process involved:
1.  **Static Analysis**: analyzing source code structure, dependencies, and metrics.
2.  **Dynamic Analysis**: Tracing execution flows (simulated based on code review).
3.  **Data Analysis**: Inspecting text file formats and data relationships.
4.  **Documentation Review**: Cross-referencing code with available legacy documentation.

## 3. Legacy System Architecture

### 3.1 High-Level Overview
The legacy system is a standalone desktop application built using Java Swing. It follows a monolithic architecture with tight coupling between the Presentation (GUI), Business Logic, and Data Access layers.

**Architecture Style**: Monolithic Desktop Application
**Technology Stack**: Java 8, Swing, AWT, File System (Text Files)

### 3.2 Package Structure
The system uses a flat package structure (default package) for most classes, with some organization in the `Database` and `Documentation` folders.

*   `src/`: Contains all `.java` source files.
*   `Database/`: Contains `.txt` data files.

### 3.3 Class Diagram (Extracted)
The following key classes and relationships were identified:

*   **POSSystem**: The central "God Class" that manages authentication, session, and main navigation. It depends on almost all other classes.
*   **Inventory**: A Singleton class managing `Item` objects and file I/O for `itemDatabase.txt`.
*   **EmployeeManagement**: Manages `Employee` CRUD operations.
*   **PointOfSale** (Abstract): Base class for transaction types.
    *   **POS**: Handles Sales transactions.
    *   **POR**: Handles Rental transactions.
    *   **POH**: Handles Return transactions.
*   **Item**: POJO representing an inventory item.
*   **Employee**: POJO representing a user.
*   **GUI Classes**: `Login_Interface`, `Cashier_Interface`, `Admin_Interface`, etc., which directly instantiate business logic classes.

## 4. Code Smells Identified

### 4.1 Architectural Smells
*   **No Layer Separation**: GUI classes (e.g., `Cashier_Interface`) contain business logic and directly manipulate data.
*   **Tight Coupling**: Classes are tightly coupled to specific file paths (e.g., "Database/employeeDatabase.txt" hardcoded in multiple places).

### 4.2 Design Smells
*   **God Class**: `POSSystem.java` handles authentication, logging, navigation, and file recovery. It has low cohesion and high coupling.
*   **Singleton Abuse**: `Inventory` is implemented as a Singleton but mixes state management with data access.

### 4.3 Implementation Smells
*   **Empty Catch Blocks**: Numerous instances of `catch(IOException e) {}` where errors are swallowed silently.
*   **Magic Numbers**: Hardcoded tax rates (e.g., `0.13`) and file paths scattered throughout the code.
*   **Duplicate Code**: File reading/writing logic is repeated in `Inventory`, `EmployeeManagement`, and `POSSystem`.
*   **Primitive Obsession**: Dates and currency are often handled as Strings or primitives without validation.

## 5. Data Analysis & Smells

### 5.1 Data Storage
Data is stored in plain text files using space or newline delimiters.

*   `employeeDatabase.txt`: Stores user credentials.
*   `itemDatabase.txt`: Stores inventory.
*   `saleInvoiceRecord.txt`: Stores transaction history.

### 5.2 Data Smells
*   **Lack of Integrity**: No foreign keys or constraints. It's possible to have a sale for a non-existent item.
*   **Redundancy**: Customer information is duplicated across transaction files.
*   **Security Risk**: Passwords are stored in plain text in `employeeDatabase.txt`.
*   **Concurrency Issues**: No file locking mechanism; concurrent writes would corrupt data.

## 6. Business Logic Recovery

### 6.1 Authentication Workflow
1.  User enters credentials in `Login_Interface`.
2.  `POSSystem` reads `employeeDatabase.txt` line by line.
3.  Matches username and password (plain text).
4.  If successful, writes to `employeeLogfile.txt` and opens appropriate dashboard.

### 6.2 Sales Workflow
1.  Cashier enters Item ID in `POS` interface.
2.  System checks `Inventory` (in-memory list loaded from file).
3.  Calculates total.
4.  On checkout, updates in-memory inventory and appends to `saleInvoiceRecord.txt`.
5.  Overwrites `itemDatabase.txt` with new stock levels.

## 7. Conclusion
The legacy system is fragile and difficult to maintain due to high coupling and poor data management. The reengineering effort must prioritize:
1.  Decoupling the UI from logic.
2.  Moving from text files to a relational database.
3.  Implementing proper error handling and logging.
