from django import forms
from .models import Return

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ['original_sale', 'reason', 'refund_amount']
        widgets = {
            'original_sale': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'refund_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
