import re
from django.core.files.storage import Storage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from apps.users.models import User, Address
from django.http import JsonResponse
# class UsernameCountView(View):
#
#     def get(self,request,username):
#         # 1.根据username进行数量的查询
#         count = User.objects.filter(username=username).count()
#         # 2.讲查询数据返回
#         return JsonResponse({"code":0,"errmsg":"ok","count":count})
# # Create your views here.
from utils.views import LoginRequiredJSONMixin


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})

    #######################注册功能########################


class Register_View(View):
    """
    1.接受数据
    2.提取数据
    3.验证数据
    4.保存数据到MYSQL
    5.状态保持
    6.反回响应
    """

    def post(self, request):
        # 1.接受请求
        body = request.body
        body_str = body.decode()
        import json
        body_dic = json.loads(body_str)

        # 2.提取参数
        username = body_dic.get("username")
        password = body_dic.get("password")
        password2 = body_dic.get("password2")
        mobile = body_dic.get("mobile")
        allow = body_dic.get("allow")

        """
        ----------3.验证参数---------

        """
        # 3.1 提取的变量都必须有值
        if not all([username, password, password2, mobile, allow]):
            # all(iterable) 函数
            # 用于判断给定的可迭代参数，若迭代序列中所有值都不为0、空、None、False 外都算True
            return JsonResponse({"code": 400, "errmsg": "参数不全"})

        # 3.2 验证用户名
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return JsonResponse({"code": 400, "errmsg": "无效名字"})
        # 3.3 验证密码是否符合规则
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({"code": 400, "errmsg": "密码无效"})
        # 3.4 验证密码和确认密码是否一致
        if password2 != password:
            return JsonResponse({"code": 400, "errmsg": "密码不一致"})
        # 3.5 验证手机号码是否符合
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({"code": 400, "errmsg": "电话号码错误"})
        """
        ----------4.保存数据到MySQL---------

        """
        # 可以进行用户密码加密
        user = User.objects.create_user(username=username,
                                        password=password,
                                        mobile=mobile
                                        )

        """
         ----------5.状态保持session redis---------

        """
        # django自带后台 -- 后台也是采用session技术
        # django 实现了session状态保持
        from django.contrib.auth import login
        # 参数1  request 请求
        # 参数2  user 用户信息

        login(request, user)

        return JsonResponse({'code': 0, 'errmsg': 'OK'})


###############################登录功能##############################
class LoginView(View):
    def post(self, request):
        # 1.接受参数
        import json
        data = json.loads(request.body.decode())
        # 2.提取参数
        username = data.get("username")
        password = data.get("password")
        remembered = data.get("remembered")
        # 判断输入的是用户名还是手机号
        # username为手机好,进行mobile判断
        # username为用户名,进行username判断
        if re.match("1[3-9]\d{9}", username):
            User.USERNAME_FIELD = "mobile"
        else:
            User.USERNAME_FIELD = "username"

        # 3.验证参数

        # 4.认证登录用户
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({"code": 400, "errmsg": "电话号码错误"})
        # 5.状态保持
        from django.contrib.auth import login
        login(request, user)
        # 6.选择是否记住登录
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        response = JsonResponse({'code': 0, 'errmsg': 'OK'})
        response.set_cookie("username", username, max_age=14 * 24 * 3600)
        return response


##################################登录退出#######################################

class LogoutView(View):
    def delete(self, request):
        # 删除状态保持信息
        from django.contrib.auth import logout
        logout(request)

        # 把username的cookie信息删除
        response = JsonResponse({"code": 0, "errmsg": "ok"})
        response.delete_cookie("username")
        return response


###########################用户中心必须用户登录才可以访问##############################
# 实现个人中心展示
# LoginRequiredMixin做了什么?
# 如果

class UserCenter(LoginRequiredJSONMixin, View):
    def get(self, request):
        # 1.判断必须是登录用户

        # 2.获取用户信息
        # 3.返回数据
        # request.user 及request中有一个属性是user,系统根据我们的session信息系统自动添加的

        user = request.user
        user_info = {
            "username": user.username,
            "mobile": user.mobile,
            "email": user.email,
            "email_active": user.email_active
        }
        return JsonResponse({"code": 0, "errmsg": "ok", "info_data": user_info})


######################################邮件保存######################################
from utils.views import LoginRequiredJSONMixin


class Email(LoginRequiredJSONMixin, View):
    def put(self, request):
        # 1.判断是否登录
        # 2.接受请求
        import json
        data = json.loads(request.body.decode())
        # 3.提取参数
        email = data.get("email")
        # 4.验证参数
        # 5.更新用户信息(添加邮箱)
        user = request.user
        user.email = email
        user.save()

        # 6.发送激活邮件
        # 需要先设置邮件服务器
        # from django.core.mail import send_mail
        # # 邮件主题
        # subject = "主题"
        # #
        # message = "邮件内容"
        # from_email = "美多商城<qi_rui_hua@163.com>"
        # # 收件人邮箱列表
        # recipient_list = ["1054416918@qq.com"]
        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_message)
        # 生成一个html
        from apps.users.utils import generic_user_id
        token = generic_user_id(user.id)
        verify_url = "http://www.meiduo.site:8080/success_verify_email.html?token=%s" % token
        html_message = "<p>尊敬的用户您好!</p>" \
                       "<p>感谢您使用美多商城!</p>" \
                       "<p>您的邮箱为:%s 请点击此链接激活您的邮箱</p>" \
                       "<p><a href=%s>%s</a></p>" % (email, verify_url, verify_url)
        from celery_tasks.email.tasks import celery_send_email
        celery_send_email.delay(html_message)

        # 7.返回响应

        return JsonResponse({"code": 0, "errmsg": "ok"})

############################################################


class VerifyEmail(View):
    def put(self, request):
        # 1. 接受请求
        data = request.GET
        # 2. 提取数据
        token = data.get("token")
        # 3. 对数据解密
        from apps.users.utils import check_user_id
        user_id = check_user_id(token)

        # 4.判断有没有user_id
        if user_id is None:
            return JsonResponse({'code': 400, 'errmsg': '链接时效'})

        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '链接时效'})

        user.email_active = True
        user.save()

        return JsonResponse({'code': 0, 'errmsg': 'ok'})

        pass


#################地址管理####################

class CreateAddress(LoginRequiredJSONMixin, View):
    def post(self, request):
        # 1.必须是登录用户
        # 2.接受参数
        import json
        data = json.loads(request.body.decode())
        # 3.提取参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 4.参数验证

        # 5.数据入库

        address = Address.objects.create(
            user=request.user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email
        )

        # 6.返回响应
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return JsonResponse({'code': 0, 'errmsg': '新增地址成功', 'address': address_dict})


###########################地址展示#######################

class AddressList(LoginRequiredJSONMixin, View):
    def get(self, request):
        # 1.判断是否是登录用户
        # 2.根据用户信息查询地址信息
        addresses = Address.objects.filter(user=request.user, is_deleted=False)

        # 3.需要对查询结果集进行遍历,装换为字典列表
        addresses_list = []
        for item in addresses:
            addresses_list.append({
                "id": item.id,
                "title": item.title,
                "receiver": item.receiver,
                "province": item.province.name,
                "city": item.city.name,
                "district": item.district.name,
                "place": item.place,
                "mobile": item.mobile,
                "tel": item.tel,
                "email": item.email
            })

        # 4.返回响应
        return JsonResponse({'code': 0,
                             'errmsg': 'ok',
                             'addresses': addresses_list,
                             'default_address_id': request.user.default_address_id})
        pass
