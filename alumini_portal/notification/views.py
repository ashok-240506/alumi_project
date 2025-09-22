from django.shortcuts import render

from .utils import notify_all_alumni

def form_valid(self, form):
    job = form.save(commit=False)
    job.posted_by = self.request.user
    job.save()

    notify_all_alumni(job, self.request.user)

    return super().form_valid(form)
