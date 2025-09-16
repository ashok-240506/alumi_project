from django import forms
from django.contrib.auth import authenticate

from adminpanel.models import Batch
from .models import RoleMaster, UserPersonalProfile
class MobileForm(forms.Form):
    mobile_number = forms.CharField(
        label='Mobile or Email',
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': ' ',
            'autocomplete': 'off',
        })
    )
class OTPForm(forms.Form):
    otp = forms.CharField(
        label="OTP",
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter OTP',
        })
    )


class SetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password")
        pw2 = cleaned_data.get("confirm_password")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data




class SignupForm(forms.Form):
    mobilenumber = forms.CharField(
        max_length=10,
        min_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'pattern': '[0-9]{10}',
            'title': 'Enter a valid 10-digit mobile number',
            'maxlength': '10',
        })
    )
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)

    roll_no = forms.CharField(required=True)
    reg_no = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    address = forms.CharField(widget=forms.Textarea, required=False)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    firstname = forms.CharField(required=True)
    lastname = forms.CharField(required=True)
    gender = forms.ChoiceField(
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        required=True
    )
    age = forms.IntegerField(required=False)
    language = forms.CharField(required=False)      
    major = forms.CharField(required=False)          
    college_name = forms.CharField(required=False)   
    university_name = forms.CharField(required=False)
    profilephoto = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-input'})
    )

    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(),
        empty_label="Select Batch",
        required=True
    )

    def clean_mobilenumber(self):
        mobilenumber = self.cleaned_data.get('mobilenumber')
        if not mobilenumber.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if len(mobilenumber) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return mobilenumber

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm_password = cleaned.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email


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


from django import forms
from .models import CustomUser, UserPersonalProfile

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "roll_no", "reg_no", "mobilenumber", "email",
            "address", "date_of_birth", "is_alumini"
        ]
        widgets = {
            "roll_no": forms.TextInput(attrs={"class": "form-input"}),
            "reg_no": forms.TextInput(attrs={"class": "form-input"}),
            "mobilenumber": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "address": forms.Textarea(attrs={"rows": 2, "class": "form-input"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "is_alumini": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class UserPersonalProfileForm(forms.ModelForm):
    class Meta:
        model = UserPersonalProfile
        fields = [
            "firstname", "lastname", "gender", "age", "language",
            "major", "batch", "college_name", "university_name", "profilephoto"
        ]
        widgets = {
            "firstname": forms.TextInput(attrs={"class": "form-input"}),
            "lastname": forms.TextInput(attrs={"class": "form-input"}),
            "gender": forms.Select(
                choices=[("Male","Male"),("Female","Female"),("Other","Other")],
                attrs={"class": "form-select"}
            ),
            "age": forms.NumberInput(attrs={"class": "form-input"}),
            "language": forms.Textarea(attrs={"rows": 2, "class": "form-input"}),
            "major": forms.TextInput(attrs={"class": "form-input"}),
            "batch": forms.Select(attrs={"class": "form-select"}),
            "college_name": forms.TextInput(attrs={"class": "form-input"}),
            "university_name": forms.TextInput(attrs={"class": "form-input"}),
            "profilephoto": forms.ClearableFileInput(attrs={"class": "form-input"}),
        }

