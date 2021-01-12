import json

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
        set = redis_cli.smembers("selected_%s" % user.id)
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

        # 获取当前要保存的订单数据
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 校验参数
        if not all([address_id, pay_method]):
            return HttpResponseBadRequest('缺少必传参数')
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return HttpResponseBadRequest('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return HttpResponseBadRequest('参数pay_method错误')

        # 获取登录用户
        user = request.user
        # 生成订单编号：年月日时分秒+用户编号
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # %09d生成个9位数包含user.id,不满足9位,用0补齐 000000001
        # 支付状态
        if pay_method == OrderInfo.PAY_METHODS_ENUM["CASH"]:
            status = OrderInfo.ORDER_STATUS_ENUM["UNPAID"]
        # 运费
        from decimal import Decimal
        freight = Decimal("10")  # 货币类型能保证金额的正确

        total_count = 0
        total_amount = Decimal("0")

        # 事物起始点
        with transaction.atomic():
            save_id = transaction.savepoint()

            # 保存订单基本信息 OrderInfo（一）
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=0,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status
            )

            # 从redis读取购物车中被勾选的商品信息
            # 连接redis
            redis_conn = get_redis_connection('carts')
            # 获取hash和set数据
            redis_cart = redis_conn.hgetall('carts_id_%s' % user.id)
            selected = redis_conn.smembers('selected_%s' % user.id)
            # 获取勾选商品信息
            carts = {}
            for sku_id in selected:
                carts[int(sku_id)] = int(redis_cart[sku_id])
            sku_ids = carts.keys()

            # 遍历购物车中被勾选的商品信息
            for sku_id in sku_ids:
                # 查询SKU信息
                sku = SKU.objects.get(id=sku_id)

                # 读取原始数据的过程
                origin_stock = sku.stock
                origin_sales = sku.sales

                # 判断SKU库存
                order_sku_count = carts[sku.id]
                if order_sku_count > sku.stock:

                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'code': 400, 'errmsg': '库存不足'})
                # 事物回滚点

                # SKU减少库存，增加销量
                # sku.stock -= order_sku_count
                # sku.sales += order_sku_count
                # sku.save()
                new_stock = origin_stock - order_sku_count
                new_sales = origin_sales - order_sku_count

                # 保存订单商品信息 OrderGoods（多）
                OrderGoods.objects.create(
                    order=order,
                    sku=sku,
                    count=order_sku_count,
                    price=sku.price,
                )

                # 保存商品订单中总价和总数量
                order.total_count += order_sku_count
                order.total_amount += (order_sku_count * sku.price)

            # 添加邮费和保存订单信息
            order.total_amount += order.freight
            order.save()
        # 事物提交点
        transaction.savepoint_commit(save_id)

        # 清除购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *selected)
        pl.srem('selected_%s' % user.id, *selected)
        pl.execute()

        # 响应提交订单结果
        return JsonResponse({'code': 0, 'errmsg': '下单成功', 'order_id': order.order_id})



