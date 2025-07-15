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
        start = int(cleaned_data.get('start_year'))
        end = int(cleaned_data.get('end_year'))

        if start > end:
            raise forms.ValidationError("Start year cannot be after end year.")