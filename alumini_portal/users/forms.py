from django import forms
from django.contrib.auth import authenticate

from adminpanel.models import Batch
from .models import RoleMaster
class MobileForm(forms.Form):
    mobile_number = forms.CharField(max_length=15)

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)

class SetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)



class SignupForm(forms.Form):
    mobilenumber = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    roll_no = forms.CharField()
    reg_no = forms.CharField()
    email = forms.EmailField()
    address = forms.CharField(widget=forms.Textarea)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    # Personal profile
    firstname = forms.CharField()
    lastname = forms.CharField()
    gender = forms.ChoiceField(choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    age = forms.IntegerField()
    language = forms.CharField()
    major = forms.CharField()
    college_name = forms.CharField()
    university_name = forms.CharField()

    # Batch dropdown instead of batch_id
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), empty_label="Select Batch")

    # Role dropdown instead of raw string
    role_type = forms.ModelChoiceField(
        queryset=RoleMaster.objects.exclude(role_type='admin'),
        to_field_name='role_type',
        empty_label="Select Role"
    )

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm_password = cleaned.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class LoginForm(forms.Form):
    mobilenumber = forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter mobile number',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter password',
            'class': 'form-control'
        })
    )

class AdminSignupForm(forms.Form):
    mobilenumber = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()
    address = forms.CharField(widget=forms.Textarea)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}) 
    )

    # Only allow admin role
    role= forms.ModelChoiceField(
        queryset=RoleMaster.objects.filter(role_name='Admin'),
        to_field_name='role_name',
        empty_label="Select Role",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
