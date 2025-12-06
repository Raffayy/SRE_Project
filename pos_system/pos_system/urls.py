"""
URL configuration for POS System project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('employees/', include('employees.urls')),
    path('rentals/', include('rentals.urls')),
    path('returns/', include('returns.urls')),
]
