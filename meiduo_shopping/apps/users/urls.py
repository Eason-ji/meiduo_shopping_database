from django.urls import path
from apps.users import views

urlpatterns = [
    path('username/<uc:username>/count/',views.UsernameCountView.as_view()),
    path("register/",views.Register_View.as_view()),
    path("login/",views.LoginView.as_view()),
    path("logout/",views.LogoutView.as_view()),
    path("info/",views.UserCenter.as_view()),
    path("emails/",views.Email.as_view()),
    path("emails/verification/",views.VerifyEmail.as_view())





]