from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from apps.goods.models import SKU
from apps.users.models import Address
from utils.views import LoginRequiredJSONMixin

"""
需求:
1.在支付页面显示用户地址信息
2.显示支付方式
3.显示产品的相关信息

流程:
0.获取用户信息
1.获取地址信息
    1.1 查询登录用户的地址信息
    1.2 将对象列表转换为字典列表
2.获取购物车中选中商品信息
    2.1 连接redis
    2.2 获取set
    2.3 获取hash
    2.4 遍历选中商品的id
    2.5 查询商品信息
3.运费
4.组织数据返回响应

URL:orders/settlement/
"""
class Order(LoginRequiredJSONMixin, View):
    def get(self,request):
        # 1.获取用户信息
        user = request.user
        # 2.获取地址信息
        # 2.1 查询登录用户的地址信息
        addresses = Address.objects.filter(user=user, is_deleted = False)
        # 2.2 对象字典转为字典列表
        address_list = []
        for item in addresses:
            address_list.append({
                "id":item.id,
                "province":item.province.name,
                "city":item.city.name,
                'district': item.district.name,
                'place': item.place,
                'receiver': item.receiver,
                'mobile': item.mobile
            })
        # 3 获取购物车中的选中商品信息
        # 3.1 连接redis
        redis_cli = get_redis_connection("carts")
        # 3.2 获取hash类型数据
        hash = redis_cli.hgetall("carts_id_%s"% user.id)
        # 3.3 获取set类类型数据
        set = redis_cli.smembers("selected_%s"% user.id)
        # 3.4 遍历选中的商品id,并从hash类型数据中提取商品的信息
        sku_list = []
        for key in set:
            sku = SKU.objects.get(id=key)
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'default_image_url': sku.default_image.url,
                'count': int(hash[key]),
                'price':sku.price
            })
        # 4. 运费
        freight = 10
        # 5.组织数据返回响应

        context = {
            "addresses": address_list,
            "skus": sku_list,
            "freight":freight
        }

        return JsonResponse({'code':0,'errmsg':'ok','context':context})


#################保存订单###############
"""
需求:
订单表:主键,user,地址,支付方式,订单状态,订单生成时间,
      订单修改时间,商品id,商品价格,商品购买数量,订单总价格

流程:


URL:/orders/commit/   POST
"""