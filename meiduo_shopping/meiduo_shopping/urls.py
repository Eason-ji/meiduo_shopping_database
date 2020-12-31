"""meiduo_shopping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
def test(request):

    import logging
    # 2.根据配置信息，创建日志
    logger=logging.getLogger('django')  # getLogger配置文件中的日志器
    # 3. 记录日志
    # 3.1 如果有错误
    logger.warning('warning')
    # 3.2 如果有错误
    logger.error('')
    # 3.3 如果记录信息
    logger.info('123')

    return HttpResponse('aaaa')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/',test)
]
