import re

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from apps.users.models import User
from django.http.response import JsonResponse




######################判断名字#########################
class UsernameCountview(View):
    # usernames/<username>/count/
    def get(self,request,username):

        # 根据username进行数量的查询
        count = User.objects.filter(username=username).count()

        return JsonResponse({"code":0,"errmsg":"ok","count":count})

######################判断电话号码#########################
class UserMobile(View):
    # mobiles / < mobile > / count /
    def get(self, request, mobile):

        # 根据mobiles进行数量查询
        count = User.objects.filter(mobile=mobile).count()

        return JsonResponse({"code":0,"errmsg":"ok","count":count})

######################实现注册功能#########################
class RegisterView(View):

    def post(self,request):
    # 1.接受参数
        body = request.body
        body_str = body.decode()
        import json
        data = json.loads(body_str)

    # 2.提取数据
        username = data.get("username")
        password = data.get("password")
        password2 = data.get("password2")
        mobile = data.get("mobile")
        allow = data.get("allow")

    # 3.验证参数
        # 3.1 验证五个变量都有数据
        if not all([username,password,password2,mobile,allow]):
            return JsonResponse({"code":400,"errmsg":"参数不齐"})
        # 3.2 验证姓名的有效
        if not re.match("[a-zA-Z0-9_-]{5,20}",username):
            return JsonResponse({"code":400,"errmsg":"输入用户名无效"})
        # 3.3 验证密码的有效
        if not re.match("[a-zA-Z0-9]{8,20}",password):
            return JsonResponse({"code":400,"errmsg":"输入密码无效"})
        # 3.4 验证重复密码的一致性
        if password2 != password:
            return JsonResponse({"code": 400, "errmsg": "两次密码输入不一致"})
        # 3.5 验证电话号码的有效性
        if not re.match("1[0-9]{10}",mobile):
            return JsonResponse({"code":400,"errmsg":"输入用户名无效"})
    # 4.数据入库
        # 增加数据
        # user = User(username=username,password=password,mobile=mobile)
        # user.save()
        # user = User.objects.create(username=username,password=password,mobile=mobile)
        # 以上两种方法密码不加密
        user = User.objects.create_user(username=username,password=password,mobile=mobile)
    # 5.状态保持
        from django.contrib.auth import login
        # 参数1：request  请求对象
        # 参数2：user     用户信息
        login(request,user)
    # 6.返回响应
        return JsonResponse({"code":0,"errmsg":"ok"})

