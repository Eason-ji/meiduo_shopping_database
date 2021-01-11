from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from apps.goods.models import SKU
from apps.users.models import Address
from utils.views import LoginRequiredJSONMixin

"""
需求:
1.在支付页面显示用户地址信息(获取用户地址信息)
2.显示支付方式
3.显示被选定产品的相关信息(获取产品相关信息)
4.显示运费

流程:
1.获取用户数据
2.根据用户信息查询用户地址信息
3.根据用户信息查询被选定商品信息
4.设置运费
5.组织数据返回响应

URL:orders/settlement/
"""
class Order(View):
    def get(self, request):
        # 获取用户信息
        user = request.user
        # 获取地址信息
        addresses = Address.objects.filter(user=user, is_deleted = False)
        address_list = []
        for address in addresses:
            address_list.append({
                "id":address.id,
                "province":address.province.name,
                "city":address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile
            })
        # 查询商品信息
        redis_cli = get_redis_connection("carts")
        hash = redis_cli.hgetall("carts_%s"%user.id)
        set = redis_cli.smember("selected_%s"%user.id)
        sku_list = []
        for key in hash:
            sku = SKU.objects.get(id=key)
            sku_list.append({
                'id':sku.id,
                'name':sku.name,
                'default_image_url': sku.default_image.url,
                'count': int(hash[key]),
                'price':sku.price
            })
        # 运费
        freight = 10

        # 组织数据返回响应
        context = {
            "addresses": address_list,
            "skus": sku_list,
            "freight":freight
        }
        return JsonResponse({'code':0,'errmsg':'ok','context':context})