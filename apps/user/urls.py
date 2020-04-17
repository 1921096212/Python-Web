from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # 注册
    path('registers/', views.Register.as_view(), name='register'),
    # 登录
    path('login/', views.Login.as_view(), name='login'),
    # 登出
    path('logout/', views.Logout.as_view(), name='logout'),

    # ----------------------------后来添加的功能----------------------------
    # 上传文件功能
    path('upload/', views.upload, name='upload'),
    # 小练习
    # path('test/', views.Test.as_view(), name='test'),
    # json接口路由
    path('api/', views.api_view),
    # 获取游客公网ip
    path('getip/', views.params_first),
    # 名言警句接口
    path('catchphrase/', views.catchphrase),
    # 手机APP启动时的画面
    path('index', views.index),

]
