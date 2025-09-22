from datetime import date
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
import random
from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

from chats.models import ChatRoom
from .models import CustomUser,OTP, RoleMapping, RoleMaster, UserPersonalProfile 
from django.views.generic import TemplateView
from .forms import  *
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .utils import *
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.views.generic import ListView

class FrontPageView(TemplateView):
    template_name = 'homepage/frontpage.html'

class StudentHomeView(TemplateView):
    template_name = 'users/student_home.html'

    def dispatch(self, request, *args, **kwargs):
        user_role = RoleMapping.objects.filter(user=request.user).first()
        if not user_role or user_role.role.role_name.lower() != 'student':
            storage = messages.get_messages(request)
            for _ in storage:
                pass
            messages.error(request, "You are not authorized as student.")
            return redirect('student_login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_alumini'] = False
        print(context)
        return context


class AlumniHomeView(TemplateView):
    template_name = 'users/student_home.html' 

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_alumini:
            storage = messages.get_messages(request)
            for _ in storage:
                pass
            messages.error(request, "You are not authorized as alumni.")
            return redirect('student_login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_alumini'] = True
        return context
    
def student_list(request):
    student_qs = (
        CustomUser.objects.filter(is_active=True, is_staff=False,is_alumini=False)
        .prefetch_related("userdetails__batch__department")
    ).exclude(id=request.user.id)

    student_data = []
    for stud in student_qs:
        details = stud.userdetails.first() if stud.userdetails.exists() else None
        student_data.append({
            "id":stud.id,
            "username": details.get_full_name(),
            "roll_no": stud.roll_no,
            "email": stud.email,
            "phone_number": stud.mobilenumber,
            "department": details.batch.department.name if details and details.batch else "",
            "batch": details.batch.name if details and details.batch else "",
            "college": details.college_name if details else "",
            "university": details.university_name if details else "",
            "profile_photo": details.profilephoto.url if details and details.profilephoto else "",
        })

    return render(request, "users/student_data.html", {"student": student_data})

def alumni_list(request):
    alumni_qs = (
        CustomUser.objects.filter(is_alumini=True, is_active=True, is_staff=False)
        .prefetch_related("userdetails__batch__department")
    ).exclude(id=request.user.id)
    alumni_data = []
    for alum in alumni_qs:
        details = alum.userdetails.first() if alum.userdetails.exists() else None
        room = ChatRoom.objects.filter(
            is_group=False,
            participants=request.user
        ).filter(participants=alum).first()
        alum.chat_room_id = room.id if room else None
        alumni_data.append({
            "id":alum.id,
            "username": details.get_full_name(),
            "roll_no": alum.roll_no,
            "email": alum.email,
            "phone_number": alum.mobilenumber,
            "department": details.batch.department.name if details and details.batch else "",
            "batch": details.batch.name if details and details.batch else "",
            # "college": details.college_name if details else "",
            # "university": details.university_name if details else "",
            "profile_photo": details.profilephoto.url if details and details.profilephoto else "",
        })

    return render(request, "users/alumni_data.html", {"alumni": alumni_data})
class StudentListView(ListView):
    template_name = "users/student_data.html"
    context_object_name = "students"

    def get_queryset(self):
        return (
            CustomUser.objects
            .filter(is_alumini=False, is_active=True,is_staff=False)
            .prefetch_related("userdetails")
        )
    

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

            user = CustomUser.objects.filter(
                Q(mobilenumber=identifier) | Q(email=identifier)
            ).first()

            if not user:
                messages.error(request, "Account not found. Please contact admin.")
                return redirect('student_login')
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
                messages.error(request, "Failed to send OTP. Try again.")

                print(f"Failed to send OTP: {e}")
            request.session['mobile_number'] = user.mobilenumber
            messages.success(request, "OTP sent successfully.")

            print(f"OTP for {user.mobilenumber}: {otp_code}")
            return redirect(f"{reverse('verify-otp')}?new_otp=1")

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

                if otp.is_valid():
                    otp.mark_used()

                    user = CustomUser.objects.filter(mobilenumber=mobile).first()
                    if not user:
                        messages.error(request, "Account not found. Please contact admin.")
                        return redirect('student_login')

                    login(request, user)
                    messages.success(request, "Login successful.")
                    if user.is_alumini:
                        return redirect('alumni_home')
                    else:
                        return redirect('student_home')


                else:
                    messages.error(request, "OTP expired or already used.")
                    return redirect('verify-otp')

            except OTP.DoesNotExist:
                messages.error(request, "Invalid or expired OTP.")
                return redirect('verify-otp')

        messages.error(request, "Invalid form input.")
        return redirect('verify-otp')

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
                messages.error(request, "Account not found. Please contact admin.")
                return redirect('student_login')

            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(
                mobile_number=user.mobilenumber,
                code=otp_code,
                created_at=timezone.now()
            )
            print('otp',otp_code)
            request.session['reset_mobile'] = user.mobilenumber
            messages.success(request, "OTP sent successfully.")
            return redirect(f"{reverse('forgot-verify-otp')}?new_otp=1")

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
                messages.success(request, "Please Update your new password.")
                return redirect('reset-password')
            else:
                messages.error(request, "Invalid or expired OTP.")
                return redirect('forgot-verify-otp')
            
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
                messages.success(request, "Password reset successfully. You can now log in.")

                request.session.pop('reset_mobile', None)
                request.session.pop('otp_verified', None)

                return redirect('student_login')
        return render(request, 'users/reset_password.html', {'form': form})


# --------------------------
# Signup + Signin
# --------------------------

class SignupView(View):
    def get(self, request):
        return render(request, 'users/signup.html', {'form': SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            reg_no = form.cleaned_data['reg_no']

            user = CustomUser.objects.filter(reg_no=reg_no, is_active=True).first()
            if not user:
                messages.error(request, "You are not authorized to signup. Please contact Admin.")
                return redirect('/')


            user.mobilenumber = form.cleaned_data['mobilenumber']
            user.email = form.cleaned_data['email']
            user.address = form.cleaned_data.get('address') or ""
            user.date_of_birth = form.cleaned_data['date_of_birth']
            user.set_password(form.cleaned_data['password'])
            batch = form.cleaned_data['batch']
            print(batch)
            current_year = date.today().year
            if batch.end_year < current_year:  
                user.is_alumni = True
            else:
                user.is_alumni = False
            user.save()

            profile = UserPersonalProfile.objects.filter(user=user).first()
            if profile:
                for field, value in form.cleaned_data.items():
                    setattr(profile, field, value)
                profile.save()
            else:
                profile = UserPersonalProfile.objects.create(user=user, **form.cleaned_data)


            role_type = 'Student'
            try:
                role_obj = RoleMaster.objects.get(role_type=role_type)
                RoleMapping.objects.get_or_create(user=user, role=role_obj)
            except RoleMaster.DoesNotExist:
                print("Role not found. Skipping mapping.")

            login(request, user)
            return redirect('send-otp')

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
                user = CustomUser.objects.filter(Q(mobilenumber=mobilenumber)|Q(email=mobilenumber)).first()
                if check_password(password, user.password):
                    login(request, user)
                    messages.success(request, "Login successful.")
                    # check role
                    user_role = RoleMapping.objects.filter(user=user).first()
                    print(user_role,user.is_alumini)
                    if user_role and user_role.role.role_name.lower() == "student" and user.is_alumini == False:
                        return redirect('student_home')
                    elif user.is_alumini:
                        return redirect('alumni_home')
                    else:
                        messages.error(request, "You are not authorized.")
                        return redirect('student_login')
                else:
                    messages.error(request, "Incorrect password.")
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found.")
        return render(request, 'users/signin.html', {'form': form})



class SignoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('home')
    

@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.userdetails.first()  # because you used related_name='userdetails'
    except UserPersonalProfile.DoesNotExist:
        profile = None

    if request.method == "POST":
        user_form = CustomUserForm(request.POST, instance=user)
        profile_form = UserPersonalProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Profile updated successfully!")

            return redirect("profile")
    else:
        user_form = CustomUserForm(instance=user)
        profile_form = UserPersonalProfileForm(instance=profile)

    return render(request, "users/user_profile.html", {
        "user_form": user_form,
        "personal_form": profile_form,
    })
