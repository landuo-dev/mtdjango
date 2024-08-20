"""
URL configuration for django01 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from myapp import views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', views.index),
#     path('updata_jx', views.updata_jx),
#     path('updata_jg', views.updata_jg),
#     path('download_excel', views.dow_exc),
#     path('dow_exc/<str:poi_id>', views.download_excel),
#     path('jg_sync', views.sync_jg),
#     path('move_product', views.move_product),
#     path('replace_priduct', views.replace_priduct),
#     path('jx_rk', views.jx_rk),
#     path('zk_rk', views.zk_rk),
# url(r"^static/(?p<path>.*)$”，serve,settings.STATIC ROOT,name='static')
# ]

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index),
    path('push_qd/<str:poi_id>', views.push_qd),
    path('ribao/<str:username>/', views.gongzuoribao),
    path('push_qd/<str:poi_id>/<str:startTime>/<str:endTime>', views.push_qd),
    path('hangye/<str:poi_id>/<str:startTime>/<str:endTime>', views.hangye),

    path('get_tupian/', views.get_tupian, name='get_tupian'),
    path('set_tupian/', views.set_tupian, name='set_tupian'),
    path('updata_jx/<int:number>/<int:aa>', views.updata_jx),
    path('updata_name/<int:number>/<int:aa>', views.updata_name),
    path('updata_jg/<int:number>/<int:aa>', views.updata_jg),
    path('jg_sync/<int:number>/<int:aa>', views.sync_jg),
    path('download_excel/<int:number>/<int:aa>', views.dow_exc),
    path('dow_exc/<str:poi_id>', views.download_excel),
    path('download_excel_new/<str:poi_id>', views.download_excel_new),
    path('download_jx_excel/', views.download_jx_excel, name='download_jx_excel'),
    path('download_jg_excel/', views.download_jg_excel, name='download_jg_excel'),
    path('download_jzyx_excel/', views.download_jzyx_excel, name='download_jzyx_excel'),
    path('download_replace_excel/', views.download_replace_excel, name='download_replace_excel'),
    path('move_product/<int:number>/<int:aa>', views.move_product),
    path('replace_priduct/<int:number>/<int:aa>', views.replace_priduct),
    path('replace_priduct1/<int:number>/<int:aa>', views.replace_priduct1),
    path('replace_priduct2/<int:number>/<int:aa>', views.replace_priduct2),
    path('review_reply/<int:number>/<int:aa>', views.review_reply),
    path('ds/<int:number>/<int:aa>', views.ds),
    path('delds/<int:number>/<int:aa>', views.delds),
    path('get_ds/<int:number>/<int:aa>', views.get_ds),
    path('jzyx_1/<int:number>/<int:aa>', views.jzyx_1),
    path('jzyx_2/<int:number>/<int:aa>', views.jzyx_2),
    path('jx_rk/<str:number>/<int:aa>', views.jx_rk),
    path('zk_rk/<int:number>/<int:aa>', views.zk_rk),
    path('back_poi/<int:number>/<int:aa>', views.back_poi),
    path('back_jgpoi/<int:number>/<int:aa>', views.back_jgpoi),
    path('get_back_poi/<int:number>/<int:aa>', views.get_back_poi),
    path('back_Recover/<int:number>/<int:aa>', views.back_Recover),

]
