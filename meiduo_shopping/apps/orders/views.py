import json
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection
from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.views import LoginRequiredJSONMixin
from datetime import datetime

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
    def get(self, request):
        # 1.获取用户信息
        user = request.user
        # 2.获取地址信息
        # 2.1 查询登录用户的地址信息
        addresses = Address.objects.filter(user=user, is_deleted=False)
        # 2.2 对象字典转为字典列表
        address_list = []
        for item in addresses:
            address_list.append({
                "id": item.id,
                "province": item.province.name,
                "city": item.city.name,
                'district': item.district.name,
                'place': item.place,
                'receiver': item.receiver,
                'mobile': item.mobile
            })
        # 3 获取购物车中的选中商品信息
        # 3.1 连接redis
        redis_cli = get_redis_connection("carts")
        # 3.2 获取hash类型数据
        hash = redis_cli.hgetall("carts_id_%s" % user.id)
        # 3.3 获取set类类型数据
        set = redis_cli.smembers("selected_id_%s" % user.id)
        # 3.4 遍历选中的商品id,并从hash类型数据中提取商品的信息
        sku_list = []
        for key in set:
            sku = SKU.objects.get(id=key)
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'count': int(hash[key]),
                'price': sku.price
            })
        # 4. 运费
        freight = 10
        # 5.组织数据返回响应

        context = {
            "addresses": address_list,
            "skus": sku_list,
            "freight": freight
        }

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})


#################提交订单###############
"""
需求:
订单表:主键,user,地址,支付方式,订单状态,订单生成时间,
      订单修改时间,商品id,商品价格,商品购买数量,订单总价格

流程:
1.接受请求
2.提取参数
3.验证参数
4.数据入库  
    4.1 订单基本信息表
        4.1.1 生成定单id(order_id)
        4.1.2 根据支付方式设置订单状态(status)
        4.1.3 运费 10
        4.1.4 订单总数量 和 订单总金额 (先暂时都定为0,在下面遍历查询商品详细信息时再更新数据)
    4.2 订单商品信息表
        4.2.1 连接redis
        4.2.2 获取选中商品id(sku_id)
        4.2.3 获取hash数据(数量)
        4.2.4 遍历选中商品的id
        4.2.5 查询商品详细信息
        4.2.6 获取库存,判断用户购买的数据库存剩余是否满足
        4.2.6.1 不满足,则下单失败
        4.2.6.2 满足,则SKU销量增加,库存减少
        4.2.7 统计总数量和订单总金额
    4.3 统计完成后,更新订单基本信息数据
    4.4 清楚redis中选中商品的信息

5.返回响应


URL:/orders/commit/   POST

前段传递的参数:用户选中的地址id\支付方式,(订单中的商品id不用提交,我们可以根据用户信息提取)
"""


class OrderCommitView(LoginRequiredJSONMixin, View):
    """订单提交"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # -----获取登录用户-----
        user = request.user
        # -----获取参数,提取参数-----
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # -----校验参数-----
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此地址'})
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM["CASH"], OrderInfo.PAY_METHODS_ENUM["ALIPAY"]]:
            return JsonResponse({'code': 400, 'errmsg': '支付方式不正确'})

        # -----订单基本数据入库-----
        # 生成订单号
        order_id = timezone.localtime().strftime("%Y%m%d%H%M%S") + "%09d" % user.id
        # 设定订单状态
        if pay_method == OrderInfo.PAY_METHODS_ENUM["CASH"]:
            status = OrderInfo.ORDER_STATUS_ENUM["UNSEND"]
        else:
            status = OrderInfo.ORDER_STATUS_ENUM["UNPAID"]
        # 运费
        freight = Decimal('10')
        # 总数和总金额
        total_count = 0
        total_amount = Decimal("0")

        # 事物开始
        with transaction.atomic():
            # 事物开始点
            start_point = transaction.savepoint()

            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status
            )
            # -----订单商品数据入库-----
            redis_cli = get_redis_connection("carts")
            # 获取选中商品的id
            selected_id = redis_cli.smembers("selected_id_%s" % user.id)
            print(selected_id)
            # 获取hash数据
            hash_data = redis_cli.hgetall("carts_id_%s" % user.id)
            print(hash_data,type(hash_data))
            # 遍历获取商品详细数据
            for id in selected_id:
                sku = SKU.objects.get(id=id)
                # 获取商品库存,判断商品库存是否满足续需求
                mysql_stock=sku.stock
                custom_count=int(hash_data[id])

                # 若无法满足需求
                print(custom_count,type(custom_count))
                print(mysql_stock,type(mysql_stock))
                if custom_count > mysql_stock:
                    transaction.savepoint_rollback(start_point)
                    return JsonResponse({'code': 400, 'errmsg': '下单失败,库存不足'})
                # 若满足需求
                # 更新商品表的销量和库存
                # sku.sales += custom_count
                # sku.stock -= custom_count
                # sku.save()
                # 更新前先判断记录的值是否和现在查询的值一致
                # 更新前数据
                old_stock = sku.stock
                # 获取更新后数据
                new_stock = sku.stock + custom_count
                new_sales = sku.sales + custom_count
                result = SKU.objects.filter(id=id, stock=old_stock).update(sales=new_sales, stock=new_stock)
                # result = 0 更新失败时会返回的值
                # result = 1 更新成功时会返回的值
                if result == 0:
                    transaction.savepoint_rollback(start_point)
                    return JsonResponse({'code': 400, 'errmsg': '下单失败'})

                # 保存订单商品数据
                OrderGoods.objects.create(
                    order=order,
                    sku=sku,
                    count=custom_count,
                    price=sku.price
                )
                # 更新订单基本信息表商品总数和总金额
                order.total_count += custom_count
                order.total_amount += custom_count * sku.price
            order.save()
            transaction.savepoint_commit(start_point)
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'order_id': order_id})
