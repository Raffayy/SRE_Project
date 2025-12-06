from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Return
from .forms import ReturnForm

class ReturnListView(ListView):
    model = Return
    template_name = 'returns/return_list.html'
    context_object_name = 'returns'
    paginate_by = 20

class ReturnCreateView(CreateView):
    model = Return
    form_class = ReturnForm
    template_name = 'returns/return_form.html'
    success_url = reverse_lazy('return_list')
    
    def form_valid(self, form):
        from employees.models import Employee
        # Assign to first employee for demo
        form.instance.employee = Employee.objects.first()
        
        messages.success(self.request, "Return processed successfully.")
        return super().form_valid(form)
