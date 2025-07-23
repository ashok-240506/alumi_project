from django.utils import timezone
import random
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from adminpanel.models import Batch
from .models import CustomUser,OTP, RoleMapping, RoleMaster, UserPersonalProfile 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.views.generic import TemplateView
from .forms import  *
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from .utils import *
from django.core.mail import send_mail
class FrontPageView(TemplateView):
    template_name = 'homepage/frontpage.html'

@method_decorator(login_required, name='dispatch')
class StudentHomeView(TemplateView):
    template_name = 'users/student_home.html'

    def dispatch(self, request, *args, **kwargs):
        user_role = RoleMapping.objects.filter(user=request.user).first()
        if not user_role or user_role.role.role_name.lower() != 'student':
            storage = messages.get_messages(request)
            for _ in storage:  # clear previous messages
                pass
            messages.error(request, "You are not authorized as student.")
            return redirect('student_login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_alumini'] = user.is_alumini
        return context

@login_required
def alumni_data_view(request):
    return render(request, 'users/alumni_data.html') 

def admin_login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data['mobilenumber']
            password = form.cleaned_data['password']

            try:
                user = CustomUser.objects.get(mobilenumber=mobile)
                if check_password(password, user.password):
                    if has_role(user, 'admin'):
                        login(request, user)
                        return redirect('/adminpanel/home/')
                    else:
                        messages.error(request, "You are not authorized as admin.")
                else:
                    messages.error(request, "Incorrect password.")
            except CustomUser.DoesNotExist:
                messages.error(request, "User with this mobile number does not exist.")
    else:
        form = LoginForm()
    
    return render(request, 'users/adminlogin.html', {'form': form})
def admin_signup(request):
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data['mobilenumber']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            address = form.cleaned_data['address']
            date_of_birth = form.cleaned_data['date_of_birth']
            role_obj = form.cleaned_data['role']
            # Create or get user
            user, created = CustomUser.objects.get_or_create(
                mobilenumber=mobile,
                defaults={
                    'email': email,
                    'address': address,
                    'date_of_birth': date_of_birth,
                    'is_verified': True
                }
            )
            user.set_password(password)
            user.save()

            try:
                RoleMapping.objects.create(user=user, role=role_obj)
            except RoleMaster.DoesNotExist:
                print("Role not found. Skipping mapping.")

            login(request, user)
            return redirect('/adminpanel/home/')
    else:
        form = AdminSignupForm()
    return render(request, 'users/admin_signup.html', {'form': form})

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
            identifier = form.cleaned_data['mobile_number']

            # Try to get user by mobile or email
            user = CustomUser.objects.filter(
                Q(mobilenumber=identifier) | Q(email=identifier)
            ).first()

            if not user:
                return render(request, 'users/send_otp.html', {
                    'form': form,
                    'error': 'Account not found. Please contact admin.'
                })

            # Send OTP
            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(
                mobile_number=user.mobilenumber,
                code=otp_code,
                created_at=timezone.now()
            )
            try:
                if '@' in identifier:
                    # Send via email
                    send_mail(
                        subject="Your OTP Code",
                        message=f"Your OTP is {otp_code}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    print(f"OTP sent to {user.email}: {otp_code}")
                else:
                    # Send via SMS
                    mobile = '+91' + user.mobilenumber
                    # send_otp_sms(mobile, otp_code)
                    print(f"OTP sent to {mobile}: {otp_code}")
            except Exception as e:
                print(f"Failed to send OTP: {e}")
            request.session['mobile_number'] = user.mobilenumber
            print(f"OTP for {user.mobilenumber}: {otp_code}")
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

                mobile = request.session.get('mobile_number')
                user = CustomUser.objects.filter(mobilenumber=mobile).first()

                if not user:
                    return render(request, 'users/verify_otp.html', {
                        'form': form,
                        'error': 'Account not found. Please contact admin.'
                })
                login(request, user)
                return redirect('student_home')

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

class SendForgotPasswordOTPView(View):
    def get(self, request):
        return render(request, 'users/forgot_password_send_otp.html', {'form': MobileForm()})

    def post(self, request):
        form = MobileForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['mobile_number']
            user = CustomUser.objects.filter(
                Q(mobilenumber=identifier) | Q(email=identifier)
            ).first()

            if not user:
                return render(request, 'users/forgot_password_send_otp.html', {
                    'form': form,
                    'error': 'Account not found.'
                })

            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(
                mobile_number=user.mobilenumber,
                code=otp_code,
                created_at=timezone.now()
            )
            print('otp',otp_code)
            request.session['reset_mobile'] = user.mobilenumber
            return redirect('forgot-verify-otp')

        return render(request, 'users/forgot_password_send_otp.html', {'form': form})
class ForgotPasswordVerifyOTPView(View):
    def get(self, request):
        return render(request, 'users/forgot_password_verify_otp.html', {'form': OTPForm()})

    def post(self, request):
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp']
            mobile = request.session.get('reset_mobile')

            otp = OTP.objects.filter(
                mobile_number=mobile, code=otp_code, is_used=False
            ).order_by('-created_at').first()

            if otp and otp.is_valid():
                otp.mark_used()
                request.session['otp_verified'] = True
                return redirect('reset-password')
            else:
                return render(request, 'users/forgot_password_verify_otp.html', {
                    'form': form,
                    'error': 'Invalid or expired OTP.'
                })

        return render(request, 'users/forgot_password_verify_otp.html', {'form': form})
class ResetPasswordView(View):
    def get(self, request):
        if not request.session.get('otp_verified'):
            return redirect('forgot-password')
        return render(request, 'users/reset_password.html', {'form': SetPasswordForm()})

    def post(self, request):
        form = SetPasswordForm(request.POST)
        if form.is_valid() and request.session.get('otp_verified'):
            mobile = request.session.get('reset_mobile')
            user = CustomUser.objects.filter(mobilenumber=mobile).first()

            if user:
                user.set_password(form.cleaned_data['password'])
                user.save()
                login(request, user)

                request.session.pop('reset_mobile', None)
                request.session.pop('otp_verified', None)

                return redirect('student_home')

        return render(request, 'users/reset_password.html', {'form': form})


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
            roll_no = form.cleaned_data['roll_no']
            reg_no = form.cleaned_data['reg_no']
            email = form.cleaned_data['email']
            address = form.cleaned_data['address']
            date_of_birth = form.cleaned_data['date_of_birth']
            batch = form.cleaned_data['batch']   
            role_type = form.cleaned_data['role_type'] 

            user, created = CustomUser.objects.get_or_create(
                mobilenumber=mobile,
                defaults={
                    'roll_no': roll_no,
                    'reg_no': reg_no,
                    'email': email,
                    'address': address,
                    'date_of_birth': date_of_birth,
                    'is_verified': True
                }
            )
            user.set_password(password)
            user.save()

            UserPersonalProfile.objects.create(
                user=user,
                firstname=form.cleaned_data['firstname'],
                lastname=form.cleaned_data['lastname'],
                gender=form.cleaned_data['gender'],
                age=form.cleaned_data['age'],
                language=form.cleaned_data['language'],
                major=form.cleaned_data['major'],
                college_name=form.cleaned_data['college_name'],
                university_name=form.cleaned_data['university_name'],
                batch=batch
            )

            try:
                role_obj = RoleMaster.objects.get(role_type=role_type)
                RoleMapping.objects.create(user=user, role=role_obj)
            except RoleMaster.DoesNotExist:
                print("Role not found. Skipping mapping.")

            login(request, user)
            return redirect('student_home')

        return render(request, 'users/signup.html', {'form': form})


class SigninView(View):
    def get(self, request):
        return render(request, 'users/signin.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            mobilenumber = form.cleaned_data['mobilenumber']
            password = form.cleaned_data['password']

            try:
                user = CustomUser.objects.get(mobilenumber=mobilenumber)
                if check_password(password, user.password):
                    login(request, user)
                    messages.success(request, "Login successful.")
                    return redirect('student_home')
                else:
                    messages.error(request, "Incorrect password.")
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found.")
        return render(request, 'users/signin.html', {'form': form})



class SignoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('signin')