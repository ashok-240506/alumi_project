from django import forms
from .models import Job, JobComment

from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'company_name', 'location', 'job_type', 'salary', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the responsibilities, requirements, and skills',
                'rows': 5
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g. Chennai, Remote'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Expected salary'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

class JobCommentForm(forms.ModelForm):
    class Meta:
        model = JobComment
        fields = ['comment']
