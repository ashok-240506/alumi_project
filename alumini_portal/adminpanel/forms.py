from django import forms
from .models import Department, Batch

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField()

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['department', 'start_year', 'end_year']
