from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from adminpanel.models import Batch 
from django.contrib.postgres.fields import JSONField
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    
    @property
    def is_alumni_dynamic(self):
        profile = self.userdetails.first() 
        if profile and profile.batch and profile.batch.end_year:
            return date.today().year > profile.batch.end_year
        return False
    

class UserPersonalProfile(models.Model):  
    """details of user"""
    firstname=models.CharField(max_length=30,null=True,blank=True)
    lastname=models.CharField(max_length=30,null=True,blank=True)
    user=models.ForeignKey(CustomUser,related_name='userdetails',on_delete=models.CASCADE)
    profilephoto = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
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
    
    def get_full_name(self):
        name = ""

        if self.firstname:
            name = str(name) + str(self.firstname) + " "
        if self.lastname:
            name = str(name) + str(self.lastname) + " "
        return name

@receiver(post_save, sender=UserPersonalProfile)
def update_is_alumni(sender, instance, **kwargs):
    user = instance.user
    if instance.batch and instance.batch.end_year:
        user.is_alumini = date.today().year > instance.batch.end_year
        user.save(update_fields=['is_alumini'])

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


class RoleMaster(models.Model):
    role_name = models.CharField(max_length=40, unique=True)
    role_desc = models.CharField(max_length=100)
    status = models.CharField(max_length=15)
    role_type = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=20)

    def __str__(self):
        return str(self.role_name)


class RoleMapping(models.Model):
    role = models.ForeignKey(RoleMaster, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name='user_role')