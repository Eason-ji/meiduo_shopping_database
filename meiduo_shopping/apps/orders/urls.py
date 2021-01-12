from django.urls import path

from apps.orders import views

urlpatterns = [
    path("orders/settlement/",views.Order.as_view()),
    path("orders/commit/", views.OrderCommitView.as_view())

]