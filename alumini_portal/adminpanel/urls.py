from django.urls import path
from .views import UploadStudentView

urlpatterns = [
    path('upload/', UploadStudentView.as_view(), name='upload-students'),
]
