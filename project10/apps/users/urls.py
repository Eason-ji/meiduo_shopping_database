from django.urls import path
from apps.users import views




urlpatterns=[
    path('index/',views.index),
    path("username/<uc:username>/count/",views.UsernameCountview.as_view()),
    path("register/",views.RegisterView.as_view())
]