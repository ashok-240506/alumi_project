from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def job_postings_view(request):
    return render(request, 'jobs/job_postings.html')  # You'll create this template below
