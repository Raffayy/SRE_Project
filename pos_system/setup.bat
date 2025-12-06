@echo off
echo ========================================
echo POS System Setup Script
echo ========================================
echo.

echo Step 1: Creating migrations...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo ERROR: Failed to create migrations
    pause
    exit /b 1
)
echo.

echo Step 2: Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)
echo.

echo Step 3: Creating superuser...
echo Please enter superuser credentials:
python manage.py createsuperuser
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now:
echo 1. Run the server: python manage.py runserver
echo 2. Access admin: http://localhost:8000/admin
echo 3. Migrate legacy data: python migrate_legacy_data.py ../Point-of-Sale-System-master/Database
echo.
pause
