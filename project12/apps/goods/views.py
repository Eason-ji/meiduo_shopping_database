from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.goods.models import GoodsCategory, SKU
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

####################商品列表页功能实现##################
"""
需求:
1.获取某个分页下的所有数据
2.每页显示page_size个数据
3.显示出有多少页数据
4.显示当前路径(面包屑)

流程:
1.获取参数
2.提取参数
3.根据分类id获取数据
4.验证参数
5.获取该分类下的数据
6.获取分页
7.将数据转化为字典列表
8.获取面包屑
9.返回数据
"""
class ListView(View):
    def get(self, request, category_id):
        data = request.GET
        page = data.get("page")
        page_size = data.get("page_size")
        ordering = data.get("ordering")

        # 按分类id获取分类
        # 判断是否有该分类
        try :
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({"code": 400, "errmsg": "没有此分类"})

        # 验证参数
        # if page-int(page) != 0:
        #     return JsonResponse({"code": 400, "errmsg": "没有此分类"})


        # 获取该分类下的数据
        sku = SKU.objects.filter(category_id=category_id).order_by(ordering)

        # 获取分页
        from django.core.paginator import Paginator
        paginator = Paginator(sku, per_page=page_size)
        # 获取每页数据
        page_sku = paginator.page(page)
        # 获取分页书
        total_num = paginator.num_pages


        # 将数据转换为字典类型数据
        sku_list = []
        for item in page_sku:
            sku_list.append({
                "id":item.id,
                "name":item.name,
                "price":item.price,
                "default_image_url":item.default_image.url
            })

        # 获取面包屑
        from utils.goods import get_breadcrumb
        breadcrumb = get_breadcrumb(category)

        # 返回响应
        return JsonResponse({
            "code": 0,
            "errmsg": "ok",
            "breadcrumb": breadcrumb,
            "list": sku_list,
            "count": total_num,
        })

###################热销商品展示########################
"""
需求:
1.将销量最高的商品展示在热销栏
2.热销商品按销量排序
3.只展示销量前三的的产品

流程:
1.接受参数
2.提取参数
3.按分类id获取分类
4.验证分类是否存在
5.根据该分类下销量靠前三的商品
6.将数据转换为字典列表
7.返回数据

URL:hot/<category_id>/
"""


class HotGoods(View):
    def get(self,request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({"code": 400, "errmsg": "没有此分类"})

        # 验证参数
        # 获取数据
        sku = SKU.objects.filter(category_id=category_id).order_by("-sales")[0:3]

        # 讲数据转换为字典列表
        sku_list = []
        for item in sku:
            sku_list.append({
                "id":item.id,
                "name":item.name,
                "price":item.price,
                "default_image_url":item.default_image.url
            })

        return JsonResponse({
            "code":0, "errmsg":"ok", "hot_skus":sku_list
        })
