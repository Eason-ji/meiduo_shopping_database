from django.shortcuts import render

# Create your views here.
from django.views import View

from utils.goods import get_categories, get_contents


class IndexView(View):
    def get(self, request):
        # 获取分页数据
        category = get_categories()
        # 获取首页数据
        contents = get_contents()
        # 组织数据,进行渲染
        context = {
            "categories":category,
            "contents":contents
        }

        return render(request,"index.html", context)



