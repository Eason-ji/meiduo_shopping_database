import json

from django.shortcuts import render

from apps.goods.models import SKU

"""
需求:
1.必须是登录用户才可以添加购物车
2.购物车信息保存在redis中(购物车的增删改查比较频繁.redis的操作数据很快)
3.保存的信息:1.用户信息(key), 2.商品id(可以获取商品信息), 3.商品添加购物车数, 4.是否选中
4.redis选择存储类型尽量可能少的占用内存
  hash:保存所有的商品id和数量(遍历hash中的id是否在set中,在则倍选中,不在则没选中)
  set: 保存选中的商品id 
  (其他方案:)
5.新增商品数量
6.提交数据:sku_id,count,选中状态

"""
from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection
from utils.views import LoginRequiredJSONMixin


""" ********************添加购物车********************
---流程:---
1.必须是登录用户
2.获取用户信息
3.接受参数
4.提取参数
5.验证参数
6.数据入库 
  6.1连接redis
  6.2hash
  6.3set
7.返回响应

URL  cars/
"""
class Carts(LoginRequiredJSONMixin,View):

    def post(self, request):
        # 获取用户信息
        user = request.user

        # 接受参数
        import json
        data = json.loads(request.body.decode())

        # 提取参数
        sku_id = data.get("sku_id")
        count = data.get("count")

        # 验证参数
        if not all([sku_id, count]):
            return JsonResponse({"code":400, "errmsg":"缺少参数"})
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({"code":400, "errmsg":"数据错误"})
        try:
            count=int(count)
        except Exception:
            count=1
        # 数据入库
        redis_cli = get_redis_connection("carts")
        # hash
        redis_cli.hset("carts_id_%s"% user.id, sku_id, count)
        # set
        redis_cli.sadd("selected_%s"% user.id, sku_id)

        return JsonResponse({"code":0, "errmsg":"ok"})

    """ ********************展示购物车********************
    ---流程:---
    需求:
    显示出购物车中显示的商品
    商品数量,商品价格,商品是否选中[默认选中]
    
    1.必须是登录用户
    2.获取用户信息
    3.获取购物车中数据(hash)
    4.获取商品是否选中数据(set)
    5.获取购物车中所有商品id
    6.遍历查询详细信息
    7.讲获取的数据转换为字典列表
    8.返回响应
    """


    def get(self,request):
        user = request.user
        redis_cli = get_redis_connection("carts")
        # 获取hash
        carts_hash = redis_cli.hgetall("carts_id_%s"% user.id)
        # {sku.id:count}
        # 获取set
        carts_set = redis_cli.smembers("selected_%s"% user.id)
        # keys
        ids = carts_hash.keys()
        carts_list = []
        for id in ids:
            sku = SKU.objects.get(id=id)
            carts_list.append({
                "id":sku.id,
                "name":sku.name,
                "price":sku.price,
                "default_image_url":sku.default_image.url,
                "selected":id in carts_set,
                "count":int(carts_hash[id]),
                "amount":sku.price*int(carts_hash[id])
            })
        return JsonResponse({"code":0,"errmsg":"ok","cart_skus":carts_list})


    """ ********************修改购物车********************
    ---流程:---
    需求:
    以一条购物车为修改单位(包括商品id,数量,选中状态)
    
    1.必须是登录用户
    2.接受数据
    3,提取数据
    4.验证数据
    5.更新数据
      5.1 连接redis
      5.2 更新hash
      5.3 更新set
    6.返回响应
    
    URL PUT 
    """
    def put(self,request):
        user = request.user
        data = json.loads(request.body.decode())

        sku_id = data.get("sku_id")
        count = data.get("count")
        selected = data.get("selected")
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({"code":400, "errmsg":"not found"})

        redis_cli = get_redis_connection("carts")

        redis_cli.hset("carts_%s"% user.id, sku_id, count)

        if selected:
            redis_cli.sadd("selected_%s"% user.id, sku_id)
        else:
            redis_cli.srem("selected_%s"%user.id, sku_id)

        cart_sku = {
             "id":sku_id,
             "name":sku.name,
             "count":int(count),
             "selected":selected,
             "price":sku.price,
             "amount": sku.price*int(count),
             "default_image_url":sku.default_image.url
        }
        return JsonResponse({"code":0,"errmsg":"","cart_sku":cart_sku})

    """ ********************删除购物车********************
    ---流程:---
    1.必须是登录用户
    2.接受数据
    3,提取数据
    4.验证数据
    5.删除数据
      5.1 连接redis
      5.2 删除hash
      5.3 删除set
    6.返回响应
    
    URL DELETE 
    """
    def delete(self, request):
        # 获取用户信息
        user = request.user
        data = json.loads(request.body.decode())

        # 提取数据
        sku_id = data.get("sku_id")

        # 验证参数
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({"code":400, "errmsg":"not found"})

        # 删除数据
            # 连接redis
        redis_cli = get_redis_connection("carts")
            # 删除hash
        redis_cli.hdel("carts_id_%s"%user.id, sku_id)
            # 删除set
        redis_cli.srem("selected_%s"%user.id, sku_id)

        return JsonResponse({"code":0,"errmsg":"ok"})


