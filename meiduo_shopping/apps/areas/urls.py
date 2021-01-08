from django.urls import path

from apps.areas import views

urlpatterns = [
    path("areas/",views.Provience.as_view()),
    path("areas/<pk>/",views.SubArea.as_view())
]