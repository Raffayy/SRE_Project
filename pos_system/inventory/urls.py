from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('add/', views.ItemCreateView.as_view(), name='item_add'),
    path('<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_edit'),
    path('<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
]
