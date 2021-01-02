from django.urls import path
from apps.users import views

urlpatterns = [
    path('username/uc:<username>/count/',views.UsernameCountView.as_view()),
    path("register/",views.Register_View),





]