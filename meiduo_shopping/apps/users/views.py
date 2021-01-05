import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from apps.users.models import User
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


    def post(self,request):
        # 1.接受请求
        body=request.body
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
        if not all([username,password,password2,mobile,allow]):
        # all(iterable) 函数
        # 用于判断给定的可迭代参数，若迭代序列中所有值都不为0、空、None、False 外都算True
            return JsonResponse({"code":400,"errmsg":"参数不全"})

        # 3.2 验证用户名
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return JsonResponse({"code":400,"errmsg":"无效名字"})
        # 3.3 验证密码是否符合规则
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({"code":400,"errmsg":"密码无效"})
        # 3.4 验证密码和确认密码是否一致
        if password2 != password:
            return JsonResponse({"code":400,"errmsg":"密码不一致"})
        # 3.5 验证手机号码是否符合
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({"code":400,"errmsg":"电话号码错误"})
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

        login(request,user)

        return JsonResponse({'code': 0, 'errmsg': 'OK'})


###############################登录功能##############################
class LoginView(View):
    def post(self,request):
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
        if re.match("1[3-9]\d{9}",username):
            User.USERNAME_FIELD = "mobile"
        else:
            User.USERNAME_FIELD = "username"

        # 3.验证参数

        # 4.认证登录用户
        from django.contrib.auth import authenticate
        user = authenticate(username=username,password=password)
        if user is None:
            return JsonResponse({"code":400,"errmsg":"电话号码错误"})
        # 5.状态保持
        from django.contrib.auth import login
        login(request,user)
        # 6.选择是否记住登录
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        response = JsonResponse({'code': 0, 'errmsg': 'OK'})
        response.set_cookie("username",username,max_age=14*24*3600)
        return response

##################################登录退出#######################################

class LogoutView(View):
    def delete(self,request):
        # 删除状态保持信息
        from django.contrib.auth import logout
        logout(request)

        # 把username的cookie信息删除
        response = JsonResponse({"code":0, "errmsg":"ok"})
        response.delete_cookie("username")
        return response


###########################用户中心必须用户登录才可以访问##############################
# 实现个人中心展示
# LoginRequiredMixin做了什么?
# 如果

class UserCenter(LoginRequiredJSONMixin,View):
    def get(self,request):

        # 1.判断必须是登录用户

        # 2.获取用户信息
        # 3.返回数据
        # request.user 及request中有一个属性是user,系统根据我们的session信息系统自动添加的
          
        user = request.user
        user_info = {
            "username":user.username,
            "mobile":user.mobile,
            "email":user.email,
            "email_active":False
        }
        return JsonResponse({"code":0,"errmsg":"ok","info_data":user_info})

