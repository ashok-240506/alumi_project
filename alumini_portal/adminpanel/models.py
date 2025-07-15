from django.db import models

# Create your models here.
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'department'
        ordering = ['created_at']

class Batch(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='batches')
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return f"{self.department.name} ({self.start_year}-{self.end_year})"
    class Meta:
        unique_together = ('name', 'department', 'start_year')
        db_table = 'batch_details'
        ordering = ['created_at']
