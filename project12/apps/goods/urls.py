from django.urls import path

from apps.goods import views

urlpatterns = [
    path("index/",views.IndexView.as_view()),
    path("list/<category_id>/skus/",views.ListView.as_view()),
    path("hot/<category_id>/",views.HotGoods.as_view()),
    path("detail/<sku_id>/",views.Detail.as_view()),
    path("detail/visit/<category_id>/", views.CategoryVisit.as_view()),
    path("browse_histories/", views.GoodsHistory.as_view())

]