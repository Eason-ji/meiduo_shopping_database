from django.urls import path
from apps.payment import views


urlpatterns = [
    path("payment/status/", views.PaymentStatusView.as_view()),
    path("payment/<order_id>/", views.PayUrl.as_view()),

]


