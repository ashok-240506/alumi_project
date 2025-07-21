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
from .forms import (
    AdminSignupForm,
    MobileForm,
    OTPForm,
    SetPasswordForm,
    SignupForm,
    LoginForm,
)
from users.utils import has_role
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
class FrontPageView(TemplateView):
    template_name = 'homepage/frontpage.html'

@method_decorator(login_required, name='dispatch')
class StudentHomeView(TemplateView):
    template_name = 'users/student_home.html'
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
            mobile = form.cleaned_data['mobile_number']
            otp_code = str(random.randint(100000, 999999))

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
            roll_no = form.cleaned_data['roll_no']
            reg_no = form.cleaned_data['reg_no']
            email = form.cleaned_data['email']
            address = form.cleaned_data['address']
            date_of_birth = form.cleaned_data['date_of_birth']
            batch_id = form.cleaned_data['batch_id']  
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
                batch=Batch.objects.get(id=batch_id)
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
class RoleMasterAPI(APIView):
    def get(self, request):

        roles = RoleMaster.objects.all()
        data = [
            {
                'id': role.id,
                'name': role.name,
                'description': role.description,} for role in roles]
        message = 'Role details fetched successfully.'
        return Response({'status': 'success', 'message': message, 'data': data}, status=status.HTTP_200_OK)
    def post(self, request):
        role='admin'
        if role != 'admin':
            return Response({'status': 'error', 'message': 'You are not authenticated to perform this action'}, status=status.HTTP_401_UNAUTHORIZED)
        messages.success(request, "Your profile was updated successfully!")
        data = request.data
        role_name = data.get('name')
        role_desc = data.get('description')
        role_status  = data.get('status')
        role_type = data.get('role_type')
        modified_by=data.get('modified_by')

        if RoleMaster.objects.filter(role_name__iexact=role_name).exists():
            return Response({'status': 'error', 'message': ' name already exists'}, status=status.HTTP_200_OK)

        role = RoleMaster(
            role_name=role_name,
            role_desc=role_desc,
            status=role_status ,
            role_type=role_type,
            modified_by=modified_by        
        )
        role.save()
        return Response({'status': 'success', 'message': 'Role created successfully'}, status=status.HTTP_200_OK)
    