from django import forms
from django.contrib.auth import authenticate
class MobileForm(forms.Form):
    mobile_number = forms.CharField(max_length=15)

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)

class SetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)




class SignupForm(forms.Form):
    mobilenumber = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

class LoginForm(forms.Form):
    mobilenumber = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        user = authenticate(username=cleaned.get('mobilenumber'), password=cleaned.get('password'))
        if not user:
            raise forms.ValidationError("Invalid credentials")
        cleaned['user'] = user
        return cleaned


