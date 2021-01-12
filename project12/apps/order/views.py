import json
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection
from apps.goods.models import SKU
from apps.order.models import OrderInfo, OrderGoods
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
        addresses = Address.objects.filter(user=user, is_deleted=False)
        address_list = []
        for address in addresses:
            address_list.append({
                "id": address.id,
                "province": address.province.name,
                "city": address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile
            })
        # 查询商品信息
        redis_cli = get_redis_connection("carts")
        hash = redis_cli.hgetall("carts_%s" % user.id)
        set = redis_cli.smembers("selected_%s" % user.id)
        sku_list = []
        for key in hash:
            sku = SKU.objects.get(id=key)
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'count': int(hash[key]),
                'price': sku.price
            })
        # 运费
        freight = 10

        # 组织数据返回响应
        context = {
            "addresses": address_list,
            "skus": sku_list,
            "freight": freight
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})


"""
URL: POST  order/commit/
请求参数: address_id pay_method
响应结果: code/errmsg/order_id

需求:
    1.在提交订单时保存订单数据
    (订单编号,下单用户,收货地址,商品总数,订单总金额,运费,支付方式,订单状态,订单生成时间,订单修改时间)
    (商品id,商品数量,商品价格,,score,is_anonymous,is_commented)
    2.订单数据包括订单基本信息和订单商品信息
    
流程: 
    1.接受参数
    2.提取参数
    3.验证参数
    4.数据入库
        4.1 获取订单基本信息表数据
            4.1.1 生成订单id
            4.1.2 根据支付方式设置订单状态
            4.1.3 运费10
            4.1.4 订单总数量 和 订单总金额(先暂时都定为0, 在后面遍历后跟新数据)
            4.1.5 订单基本信息表数据保存
        4.2 获取订单商品信息表
            4.2.1 连接redis
            4.2.2 获取选中商品id(sku_id)
            4.2.3 获取hash数据
            4.2.4 遍历选中商品的id
            4.2.5 查询商品详细信息
            4.2.6 获取库存,判断用户购买的商品库存剩余是否满足
                a.不满足,则下单失败
                b.满足,则SKU销量增加,库存减少
            4.2.7 保存订单商品信息
            4.2.8 统计商品总数和订单总数
        4.3 统计完后更新订单基本信息数据
        4.4 删除redis中选中商品的信息

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
        if not all([address_id, pay_method]):
            return HttpResponseBadRequest('缺少必传参数')
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此地址'})
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM["CASH"], OrderInfo.PAY_METHODS_ENUM["ALIPAY"]]:
            return JsonResponse({'code': 400, 'errmsg': '支付方式不正确'})

        # -----订单基本数据入库-----
        # 生成订单号
        order_id = timezone.localtime().strftime("%Y%M%D%H%M%S") + "%09d" % user.id
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

            order = OrderInfo.objects.crea(
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
            selected_id = redis_cli.smembers("selected_%s" % user.id)
            # 获取hash数据
            hash_data = redis_cli.hegetall("carts_%s" % user.id)
            # 遍历获取商品详细数据
            for id in selected_id:
                sku = SKU.objects.get(id=id)
                # 获取商品库存,判断商品库存是否满足续需求
                mysql_stock = sku.stock
                custom_count = hash_data[id]
                # 若无法满足需求
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
                new_stock = sku.stock-custom_count
                new_sales = sku.sales+custom_count
                result = SKU.objects.filter(id=id, stock=old_stock).update(sales=new_sales, stock=new_stock)
                # result = 0 更新失败时会返回的值
                # result = 1 更新成功时会返回的值
                if result == 0:
                    transaction.savepoint_rollback(start_point)
                    return JsonResponse({'code':400,'errmsg':'下单失败'})

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
            transaction.savepoint(start_point)
        return JsonResponse({'code':0,'errmsg':'ok','order_id':order_id})