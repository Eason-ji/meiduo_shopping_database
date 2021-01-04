from django.urls import path
from apps.verifications import views

urlpatterns = [
    path("image_codes/<uuid>/",views.ImageCode.as_view()),
    path("sms_codes/<mobile>/",views.SmsCode.as_view()),
]