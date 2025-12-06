from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReturnListView.as_view(), name='return_list'),
    path('add/', views.ReturnCreateView.as_view(), name='return_add'),
]
