from django import forms
from .models import Medicine, Dispensing, StockMovement, MedicineCategory


class MedicineCategoryForm(forms.ModelForm):
    class Meta:
        model = MedicineCategory
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        exclude = ['created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class DispensingForm(forms.ModelForm):
    class Meta:
        model = Dispensing
        exclude = ['total_price', 'dispensed_at']


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        exclude = []
        widgets = {
            'reason': forms.TextInput(attrs={'placeholder': 'Reason for stock movement...'}),
        }
