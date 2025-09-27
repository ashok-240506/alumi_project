from django.urls import path
from .views import (
    JobListView, JobDetailView, JobCreateView, JobUpdateView, JobDeleteView,MyJobListView,job_all_comments,
    JobCommentCreateView, job_like,job_stats,user_notification,mark_notification_read
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
    path("notification/<int:pk>/read/", mark_notification_read, name="mark_notification_read"),
    path("<int:pk>/notification/",user_notification, name="notification"),
    path("my-jobs/", MyJobListView.as_view(), name="my_jobs"),
    path('jobs/<int:pk>/all-comments/', job_all_comments, name='job_all_comments'),



]
