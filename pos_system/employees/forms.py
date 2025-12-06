from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text="Leave blank to keep current password")
    
    class Meta:
        model = Employee
        fields = ['username', 'name', 'position', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def save(self, commit=True):
        employee = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            employee.set_password(password)
        if commit:
            employee.save()
        return employee
