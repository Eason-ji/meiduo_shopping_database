from django.urls import path
from apps.oauth.views import QQUserView

urlpatterns = [
    path("",QQUserView.as_view())
]