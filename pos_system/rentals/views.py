from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Rental
from .forms import RentalForm

class RentalListView(ListView):
    model = Rental
    template_name = 'rentals/rental_list.html'
    context_object_name = 'rentals'
    paginate_by = 20

class RentalCreateView(CreateView):
    model = Rental
    form_class = RentalForm
    template_name = 'rentals/rental_form.html'
    success_url = reverse_lazy('rental_list')
    
    def form_valid(self, form):
        # Set defaults for required fields
        from employees.models import Employee
        from decimal import Decimal
        
        # Assign to first employee for demo
        form.instance.employee = Employee.objects.first()
        form.instance.total = Decimal('0.00')
        
        messages.success(self.request, "Rental created successfully.")
        return super().form_valid(form)

class RentalUpdateView(UpdateView):
    model = Rental
    fields = ['status'] # Simple update for now
    template_name = 'rentals/rental_form.html'
    success_url = reverse_lazy('rental_list')
