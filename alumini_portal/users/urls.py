from django.urls import path
from .views import *

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('admin-signup/',admin_signup, name='admin-signup'),
    path('signin/', SigninView.as_view(), name='student_login'),
    path('signout/', SignoutView.as_view(), name='signout'),
    path('student/home/', StudentHomeView.as_view(), name='student_home'),
    path('alumini/home/', AlumniHomeView.as_view(), name='alumni_home'),
    path('alumni/data/',alumni_list, name='alumni_data'),
    path("students/data/",student_list, name="student_data"),
    path('forgot-password/', SendForgotPasswordOTPView.as_view(), name='forgot-password'),
    path('forgot-verify-otp/', ForgotPasswordVerifyOTPView.as_view(), name='forgot-verify-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path("profile/", profile_view, name="profile"),

]
