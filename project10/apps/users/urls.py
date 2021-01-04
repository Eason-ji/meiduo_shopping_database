from django.urls import path
from apps.users import views




urlpatterns=[
    path("username/<uc:username>/count/",views.UsernameCountview.as_view()),
    path("mobiles/<mb:mobile>/count/",views.UserMobile.as_view()),
    path("register/",views.RegisterView.as_view())
]