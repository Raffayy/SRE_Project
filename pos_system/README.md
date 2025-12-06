# POS System - Reengineered Web Application

Modern web-based Point-of-Sale system built with Django and PostgreSQL.

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Setup Database

```bash
# Create PostgreSQL database
createdb pos_system

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000

## Project Structure

```
pos_system/
├── manage.py
├── requirements.txt
├── pos_system/          # Project settings
├── employees/           # Employee management app
├── inventory/           # Inventory management app
├── sales/              # Sales transactions app
├── rentals/            # Rental transactions app
├── returns/            # Returns processing app
└── tests/              # Test suite
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_employees.py
```

## Admin Interface

Access the Django admin at http://localhost:8000/admin

## Technology Stack

- **Backend:** Python 3.11+ / Django 4.2+
- **Database:** PostgreSQL 15+
- **Testing:** pytest + Hypothesis
- **Frontend:** Django Templates + Bootstrap 5
