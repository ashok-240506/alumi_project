from django.urls import path
from .views import *

urlpatterns = [
    path('home/', admin_home, name='admin-home'),
    path('upload/', UploadStudentView.as_view(), name='upload-students'),
    # Department URLs
    path('departments/', DepartmentListView.as_view(), name='department-list'),
    path('departments/add/', DepartmentCreateView.as_view(), name='department-add'),
    path('departments/edit/<int:pk>/', DepartmentUpdateView.as_view(), name='department-edit'),
    path('departments/delete/<int:pk>/', DepartmentDeleteView.as_view(), name='department-delete'),

    # Batch URLs
    path('batches/', BatchListView.as_view(), name='batch-list'),
    path('batches/add/', BatchCreateView.as_view(), name='batch-add'),
    path('batches/edit/<int:pk>/', BatchUpdateView.as_view(), name='batch-edit'),
    path('batches/delete/<int:pk>/', BatchDeleteView.as_view(), name='batch-delete'),


]
