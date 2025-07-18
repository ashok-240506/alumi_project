from django import forms
from .models import Department, Batch
from datetime import datetime
class UploadExcelForm(forms.Form):
    excel_file = forms.FileField()

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']


CURRENT_YEAR = datetime.now().year
YEAR_CHOICES = [(y, y) for y in range(CURRENT_YEAR, 1979, -1)]

class BatchForm(forms.ModelForm):
    start_year = forms.ChoiceField(choices=YEAR_CHOICES)
    end_year = forms.ChoiceField(choices=YEAR_CHOICES)

    class Meta:
        model = Batch
        fields = ['department', 'start_year', 'end_year']

    def clean(self):
        cleaned_data = super().clean()
        start_year = int(cleaned_data.get('start_year'))
        end_year = int(cleaned_data.get('end_year'))
        department = cleaned_data.get('department')

        if start_year > end_year:
            raise forms.ValidationError("Start year cannot be after end year.")

        name = f"{start_year}-{end_year}"

        
        if Batch.objects.filter(
            name=name, department=department, start_year=start_year
        ).exists():
            raise forms.ValidationError(f"Batch {name} for department '{department}' already exists.")

        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.name = f"{instance.start_year}-{instance.end_year}"
        if commit:
            instance.save()
        return instance