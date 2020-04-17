from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    # 主页面
    path('', views.IndexView.as_view(), name='index'),  # 将这条路由命名为index
    # 新闻列表
    path('news/', views.NewsListView.as_view(), name='news_detail_list'),
    # 新闻详情页
    path('news/<int:news_id>/', views.NewsDetail.as_view(), name='news_detail'),
    # 轮播图
    path('news/banners/', views.BannerView.as_view(), name='news_banner'),
    # 追加评论
    path('news/<int:news_id>/comments/', views.CommentView.as_view(), name='comments'),
    # 搜索
    path('search/', views.Search(), name='search'),
]
