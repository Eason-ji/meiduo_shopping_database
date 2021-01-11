from django.urls import path
from apps.carts import views

urlpatterns = [
    path("carts/",views.Carts.as_view())
]