from django.urls import path
from . import views

urlpatterns = [
    path('', views.RentalListView.as_view(), name='rental_list'),
    path('add/', views.RentalCreateView.as_view(), name='rental_add'),
    path('<int:pk>/edit/', views.RentalUpdateView.as_view(), name='rental_edit'),
]
