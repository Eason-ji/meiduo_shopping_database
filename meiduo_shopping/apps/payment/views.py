from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from apps.orders.models import OrderInfo
from utils.views import LoginRequiredJSONMixin

"""************************支付宝支付************************
生成在支付宝支付的跳转链接
接受支付成功后支付宝返回来的订单id

生成两对公钥和私钥
自己的: 通过指令生成,私钥保存到我们的工程中,公钥上传到支付宝沙箱环境中
支付宝:公钥保存到我们的工程中

流程:
当用户点击去支付时,前台html会发送ajax请求给django,django要生成跳转url
django怎么生成跳转URL呢,根据支付宝文档生成
生成后返回给前台,前台跳转到支付宝支付

1.获取订单id
2.根据订单id查询订单
3.创建支付宝支付对象
4.生成一个order_sting(根据支付宝文档)
5.拼接支付url
6.返回支付url

url: order
"""


class PayUrl(LoginRequiredJSONMixin, View):

    def get(self, request, order_id):
        user = request.user
        # 获取订单id
        # 根据订单id查询订单
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此订单'})
        # 创建支付宝支付对象(根据文档)
        from alipay import AliPay
        from alipay.utils import AliPayConfig
        # 3.1 通过文件的形式,读取美多私钥和支付宝公钥
        # 最好设置一个相对路径,把相对路径的配置放到settings
        from meiduo_shopping import settings
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=False,  # 默认False
            config=AliPayConfig(timeout=15)  # 可选, 请求超时时间
        )
        # 4. 通过电脑网址支付的方法, 来生成 order_string
        # 如果你是 Python 3的用户，使用默认的字符串即可
        subject = "测试订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 美多商城的订单id
            total_amount=str(order.total_amount),  # 订单总金额  类型转换为 str
            subject=subject,
            return_url=settings.ALIPAY_RETURN_URL,  # 支付成功之后,最终要跳转会美多
            # notify_url="https://example.com/notify"         # 可选, 不填则使用默认notify url
        )
        # 5. 拼接url
        alipay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string

        # 6. 返回支付url
        return JsonResponse({'code': 0, 'alipay_url': alipay_url})


######################保存支付结果###################
"""
URL GET 
流程:
    1.接受参数
    2.提取参数
    3.保存入库
    4.支付成功需要修改订单状态
    5.返回响应 code/errmsg/trade_id
    

"""


class PaymentStatusView(View):
    """保存订单支付结果"""

    def put(self, request):
        # 1.接受参数
        data = request.GET
        # 2.提取参数
        out_trade_no = data.get("out_trade_no")
        trade_no = data.get("trade_no")
        # 3.保存入库
        from apps.payment.models import Payment
        Payment.objects.create(
            order_id=out_trade_no,
            trade_id=trade_no
        )
        # 4.支付成功需要修改订单状态
        OrderInfo.objects.filter(order_id=out_trade_no).update(status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])
        # 5.返回响应 code/errmsg/trade_id

        return JsonResponse({'code': 0, 'errmsg': 'OK', 'trade_id': trade_no})


"""
搜索引擎,可以把我们杂乱的数据

引擎-Elasticsearch
借助于Docker部署Elasticsearch
Docker(基于云计算的)
    1.是一个轻量级的应用容器框架
    2.c/s架构 客户端虚拟机已经安装好
             服务端:hub.docker,com
    3.三个基本概念:
        1.镜像:一个只读的模板,一个独立的文件系统
        2.容器:由Docker镜像创建的运行实例
        3.仓库:用于托管镜像

docker 容器操作
交互方式运行: sudo docker run -it 镜像名字:版本
            sudo docker run -it ubuntu:latest
            sudo权限 Docker  i  t 
            exit 退出交互模式
守护进程运行: sudo docker run -dit ubuntu:latest # 创建容器
            sudo docker run -dit --name=aaa ubuntu:latest # 设置容器名
            sudo docker container stop 容器id/名 # 停止容器
查看容器: sudo docker container ls 
         sudo docker container ls --all 罗列所有的包括退出的
启动容器:sudo docker container start 容器id
删除容器(只能删除停止的):sudo docker container rm 容器id
设置容器名字:
"""
