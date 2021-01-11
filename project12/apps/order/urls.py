from django.urls import path
from apps.order import views

urlpatterns = [
    path("orders/settlement/",views.Order.as_view()),
]