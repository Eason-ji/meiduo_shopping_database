from datetime import date

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.goods.models import GoodsCategory, SKU, GoodsVisitCount
from utils.goods import get_categories, get_contents, get_breadcrumb, get_goods_specs


class IndexView(View):
    def get(self, request):
        # 获取分页数据
        category = get_categories()
        # 获取首页数据
        contents = get_contents()
        # 组织数据,进行渲染
        context = {
            "categories": category,
            "contents": contents
        }

        return render(request, "index.html", context)


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
        try:
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
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "default_image_url": item.default_image.url
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
    def get(self, request, category_id):
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
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "default_image_url": item.default_image.url
            })

        return JsonResponse({
            "code": 0, "errmsg": "ok", "hot_skus": sku_list
        })


##########################详情页面获取#############################
"""
需求:
1.展示分类数据
2.展示SKU详细数据
3.展示SKU的规格和规格选项
4.展示面包屑

流程:
1.接受参数
2.根据sku_id进行商品查询
3.获取分类数据
4.获取面包数据
5.获取规格和规格选项
6.进行html渲染
7.返回

GET   /detail/<sku_id>/
"""

class Detail(View):
    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
            print("sku数据"+sku)
        except SKU.DoesNotExist:
            return JsonResponse({"code": 400, "errmsg": "没有次商品"})
        # 获取分类数据
        Category = get_categories()
        print("分类数据"+Category)
        # 获取面包数据
        breadcrumb = get_breadcrumb(sku.Category)
        print("面包屑数据"+breadcrumb)

        # 获取规格和规格选项
        specs = get_goods_specs(sku)

        # html渲染
        context = {
            'categories': Category,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': specs,
        }

        return render(request, "detail.html", context)

#####################统计商品分类访问量########################
"""
需求:
客户每点击一次商品就会增加该商品的访问量

流程:
1.获取分类id
2.根据分类id查询分类是否存在
3.获取当天的日期
4.根据日期和分类id查询,判断数据库中是否已经存在记录
5.若存在则记录+1
6.若不存在则添加记录
7.返回响应
"""
class CategoryVisit(View):
    def post(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return ({"code": 400, "errmsg": "not found"})

        today = date.today()

        try:
            gvc = GoodsVisitCount.objects.get(category=category, date=today)
        except GoodsVisitCount.DoesNotExist:
            GoodsVisitCount.objects.create(
                category=category,
                date = today,
                count=1
            )
        else:
            gvc.count += 1
            gvc.save()

        return JsonResponse({"code": 0, "errmsg": 'ok'})