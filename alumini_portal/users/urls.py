from django.urls import path
from .views import *

urlpatterns = [
    path('create-role/', RoleMasterAPI.as_view(), name='role-create'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('admin-signup/',admin_signup, name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('signout/', SignoutView.as_view(), name='signout'),

]
