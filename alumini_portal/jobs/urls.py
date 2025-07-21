from django.urls import path
from .views import job_postings_view

urlpatterns = [
    path('', job_postings_view, name='job_postings'),
]
