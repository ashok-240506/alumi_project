from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from adminpanel.models import Batch 
from django.contrib.postgres.fields import JSONField

class CustomUser(AbstractUser):
    username = None  
    roll_no = models.CharField(max_length=20, unique=True)#dept ID
    reg_no = models.CharField(max_length=20, unique=True)#university ID
    mobilenumber = models.CharField(max_length=32, unique=True) 
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(max_length=100, blank=True, null=True, unique=True)
    address = models.TextField()
    date_of_birth = models.DateField(blank=True, null=True)
    is_alumini = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.IntegerField(blank=True, null=True)

    USERNAME_FIELD = "mobilenumber"  
    REQUIRED_FIELDS = ["email"]  

    class Meta:
        unique_together = ("mobilenumber", "email")

class UserPersonalProfile(models.Model):  
    """details of user"""
    firstname=models.CharField(max_length=30,null=True,blank=True)
    lastname=models.CharField(max_length=30,null=True,blank=True)
    user=models.ForeignKey(CustomUser,related_name='userdetails',on_delete=models.CASCADE)
    profilephoto=JSONField(null=True,blank=True,default=dict)
    gender=models.CharField(max_length=20,null=True,blank=True)
    age=models.IntegerField(blank=True,null=True)
    language=models.TextField(blank=True,null=True)
    major = models.CharField(max_length=100)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True)
    college_name = models.CharField(max_length=150)
    university_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'user_profile_details'
        ordering = ['created_at']

class OTP(models.Model):
    mobile_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=5) and not self.is_used

    def mark_used(self):
        self.is_used = True
        self.save()