from django.urls import path
from apps.areas import views

urlpatterns = [
    path("areas/",views.Province.as_view()),
    path("areas/<pk>/", views.SubAreas.as_view()),
]