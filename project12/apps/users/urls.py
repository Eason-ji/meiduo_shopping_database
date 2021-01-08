from django.urls import path
from apps.users import views




urlpatterns=[
    path("usernames/<uc:username>/count/",views.UserName.as_view()),
    path("mobiles/<mc:mobile>/count/",views.UserMobile.as_view()),
    path("register/",views.Register.as_view()),
    path("login/",views.LoginView.as_view()),
    path("logout/",views.Logout.as_view()),
    path("info/",views.InfoView.as_view()),
    path("addresses/create/",views.CreateArea.as_view())

]