from django.urls import path
from apps.users import views




urlpatterns=[
    path("username/<username>/count/",views.UserName.as_view()),
    path("mobiles/<mobile>/count/",views.UserMobile.as_view()),
    path("register/",views.Register.as_view()),
    path("login/",views.LoginView)
]