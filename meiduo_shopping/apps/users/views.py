import re

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

        # 5.状态保持session redis
        # django自带后台 -- 后台也是采用session技术
        # django 实现了session状态保持
        from django.contrib.auth import login
        # 参数1  request 请求
        # 参数2  user 用户信息

        login(request,user)

        return JsonResponse({'code': 0, 'errmsg': 'OK'})