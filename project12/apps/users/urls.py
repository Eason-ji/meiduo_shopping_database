from django.urls import path
from apps.users import views




urlpatterns=[
    path("username/<uc:username>/count/",views.UserName.as_view()),
    path("mobiles/<mb:mobile>/count/",views.UserMobile.as_view()),
    path("register/",views.Register.as_view())
]