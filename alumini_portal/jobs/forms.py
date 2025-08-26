from django import forms
from .models import Job, JobComment

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'company_name', 'location', 'job_type', 'salary', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
class JobCommentForm(forms.ModelForm):
    class Meta:
        model = JobComment
        fields = ['comment']
