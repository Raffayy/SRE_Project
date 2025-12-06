from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Item
from .forms import ItemForm
from .services import InventoryService
from .repositories import ItemRepository

class InventoryListView(ListView):
    model = Item
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 20
    
    def get_queryset(self):
        repo = ItemRepository()
        service = InventoryService(repo)
        return service.get_all_items()

def inventory_list(request):
    repo = ItemRepository()
    service = InventoryService(repo)
    items = service.get_all_items()
    return render(request, 'inventory/item_list.html', {'items': items})

class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Item created successfully.")
        return super().form_valid(form)

class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Item updated successfully.")
        return super().form_valid(form)

class ItemDeleteView(DeleteView):
    model = Item
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('inventory_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Item deleted successfully.")
        return super().delete(request, *args, **kwargs)
