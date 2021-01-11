from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from apps.goods.models import SKU
from apps.users.models import Address
from utils.views import LoginRequiredJSONMixin



"""*********************添加购物车*********************
需求:




"""