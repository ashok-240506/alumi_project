from django.urls import path
from .views import (
    JobListView, JobDetailView, JobCreateView, JobUpdateView, JobDeleteView,
    JobCommentCreateView, job_like,job_stats
)

urlpatterns = [
    path('', JobListView.as_view(), name='job_list'),
    path('create/', JobCreateView.as_view(), name='job_create'),
    path('<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    path('<int:pk>/edit/', JobUpdateView.as_view(), name='job_edit'),
    path('<int:pk>/delete/', JobDeleteView.as_view(), name='job_delete'),
    path('<int:pk>/comment/', JobCommentCreateView.as_view(), name='job_comment'),
    path('<int:pk>/like/', job_like, name='job_like'),
    path("<int:pk>/stats/", job_stats, name="job_stats"),

]
