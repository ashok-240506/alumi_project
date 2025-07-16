from django.utils import timezone
import random
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomUser,OTP
from django.views.generic import TemplateView
from .forms import (
    MobileForm,
    OTPForm,
    SetPasswordForm,
    SignupForm,
    LoginForm,
)
from users.utils import has_role
from django.contrib import messages

class FrontPageView(TemplateView):
    template_name = 'homepage/frontpage.html'



class AdminLoginView(View):
    def get(self, request):
        return render(request, 'users/adminlogin.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            if has_role(user, 'admin'):  # using your role_type field
                login(request, user)
                return redirect('adminpanel:admin-home')
            else:
                messages.error(request, "You are not authorized as admin.")
        return render(request, 'users/adminlogin.html', {'form': form})

otp_store = {}

# --------------------------
# OTP Login Flow
# --------------------------

class SendOTPView(View):
    def get(self, request):
        return render(request, 'users/send_otp.html', {'form': MobileForm()})

    def post(self, request):
        form = MobileForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data['mobile_number']
            otp_code = str(random.randint(100000, 999999))

            # Save OTP to database
            OTP.objects.create(
                mobile_number=mobile,
                code=otp_code,
                created_at=timezone.now()
            )

            request.session['mobile_number'] = mobile
            print(f"OTP for {mobile}: {otp_code}")  # Simulate SMS
            return redirect('verify-otp')

        return render(request, 'users/send_otp.html', {'form': form})


class VerifyOTPView(View):
    def get(self, request):
        return render(request, 'users/verify_otp.html', {'form': OTPForm()})

    def post(self, request):
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp']
            mobile = request.session.get('mobile_number')

            try:
                otp = OTP.objects.filter(
                    mobile_number=mobile,
                    code=otp_code,
                    is_used=False
                ).latest('created_at')
            except OTP.DoesNotExist:
                return render(request, 'users/verify_otp.html', {
                    'form': form,
                    'error': 'Invalid or expired OTP.'
                })

            if otp.is_valid():
                otp.mark_used()

                user, created = CustomUser.objects.get_or_create(
                    mobilenumber=mobile,
                )
                user.set_unusable_password() 
                user.is_verified = True
                user.save()

                if not user.has_usable_password():
                    request.session['user_id'] = user.id
                    return redirect('set-password')
                print("Has usable password?", user.has_usable_password())

                login(request, user)
                return redirect('/')
            else:
                return render(request, 'users/verify_otp.html', {
                    'form': form,
                    'error': 'OTP expired or already used.'
                })

        return render(request, 'users/verify_otp.html', {'form': form})

class SetPasswordView(View):
    def get(self, request):
        return render(request, 'users/set_password.html', {'form': SetPasswordForm()})

    def post(self, request):
        form = SetPasswordForm(request.POST)
        user_id = request.session.get('user_id')

        if not user_id:
            return redirect('send-otp')

        user = CustomUser.objects.filter(id=user_id).first()

        if form.is_valid() and user:
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('/')

        return render(request, 'users/set_password.html', {'form': form})


# --------------------------
# Signup + Signin
# --------------------------

class SignupView(View):
    def get(self, request):
        return render(request, 'users/signup.html', {'form': SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data['mobilenumber']
            password = form.cleaned_data['password']

            user, created = CustomUser.objects.get_or_create(
                mobilenumber=mobile 
            )

            user.set_password(password)
            user.is_verified = True
            user.save()
            login(request, user)
            return redirect('/')

        return render(request, 'users/signup.html', {'form': form})


class SigninView(View):
    def get(self, request):
        return render(request, 'users/signin.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data['user'])
            return redirect('/')
        return render(request, 'users/signin.html', {'form': form})


class SignoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('signin')
