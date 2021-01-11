from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from apps.goods.models import SKU
from apps.users.models import Address
from utils.views import LoginRequiredJSONMixin
import json


"""*********************添加购物车*********************
需求:
1.必须是登录用户才可添加购物车  # 暂时不实现
2.用户点击添加购物车时讲数据保存.
2.添加购物车的商品至少需要获取商品id(可以获取商品其他信息) 数量 是否选定(默认是选定状态)三个数据
3.购物车数据存储在redis中
4.redis的hash类型数据用来存储商品id和数量; set数据用来存储被选定商品的id

流程:
1.获取数据
2.提取参数
3.获取用户信息
4.验证参数
5.数据入库
    5.1 连接redis
    5.2 添加hash数据
    5.3 添加set数据
6.返回响应
**************************************************"""
class Carts(View):
    def post(self, request):
        data= json.loads(request.body.decode())

        # 提取参数
        sku_id = data.get("sku_id")
        count = data.get("count")

        # 获取用户信息
        user = request.user
        # 验证参数
        # 数据入库
        redis_cli = get_redis_connection("carts")
        redis_cli.hset("carts_%s"%user.id, sku_id, count)
        redis_cli.sadd("selected_%s"%user.id, sku_id)

        return JsonResponse({"code": 0, "errmsg": "ok"})

    """*********************购物车展示*********************
    需求:
    显示出购物车中显示的商品
    
    流程:
    1.获取用户信息
    2.根据用户id提取redis中的购物车数据
    3.获取购物车中所有商品id
    4.遍历查询商品详细信息
    5.将获取的数据信息转换为字典列表类型数据
    6.返回响应
    """
    def get(self, request):
        user = request.user
        # 获取redis中购物车数据
        redis_cli = get_redis_connection("carts")
        hash = redis_cli.hgetall("carts_%s"% user.id)
        set = redis_cli.smembers("selected_%s"%user.id)
        # 遍历查询商品详细信息
        sku_list = []
        hash_key = hash.keys()
        for i in hash_key:
            sku = SKU.objects.get(id = i)
            sku_list.append({
                "id": sku.id,
                "name": sku.name,
                "price": sku.price,
                "default_image_url": sku.default_image.url,
                "selected": id in set,
                "count": int(hash[id]),
                "amount": sku.price * int(hash[id])
            })
        return JsonResponse({"code": 0, "errmsg": "ok", "cart_skus": sku_list})