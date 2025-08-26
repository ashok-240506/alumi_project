# jobs/models.py
from django.db import models
from users.models import CustomUser  # Use your custom user model
from django.urls import reverse
class Job(models.Model):
    JOB_TYPES = [
        ('FT', 'Full-time'),
        ('PT', 'Part-time'),
        ('IN', 'Internship'),
        ('CT', 'Contract'),
        ('RE', 'Remote'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=2, choices=JOB_TYPES)
    salary = models.CharField(max_length=100, blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='jobs')
    posted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"
    def get_absolute_url(self):
        return reverse("job_detail", kwargs={"pk": self.pk})
class JobLike(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'user')  # Prevent multiple likes per user
class JobComment(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.comment[:30]}..."