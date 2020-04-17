from django.urls import path
from . import views

# app的名字
app_name = 'admin'

urlpatterns = [
    # 后台管理主页面
    path('', views.IndexView.as_view(), name='index'),
    # 后台管理标签页面
    path('tags/', views.TagsManageView.as_view(), name='tags'),
    path('tags/<int:tag_id>/', views.TagsManageView.as_view(), name='tags_manage'),
    # 后台热门文章页面
    path('hot_news/', views.HotNewManageView.as_view(), name="hot_manage"),
    # 热门新闻修改和删除
    path('hot_news/<int:hot_news_id>/', views.HotNewManageView.as_view(), name='hot_edit'),
    # 热门新闻添加
    path('hot_news/add/', views.HotNewsAddView.as_view(), name='hot_news_add'),
    # 获取热门新闻id
    path('tags/<int:tag_id>/news/', views.NewsByTagIdView.as_view(), name='news_by_tagid'),
    # 文章管理检索等
    path('news/', views.NewsManageView.as_view(), name='news_manage'),
    # 添加文章页
    path('news_add/', views.NewsAddView.as_view(), name='news_add'),
    # 文章编辑页
    path('new/<int:news_id>/', views.NewsEditView.as_view(), name='news_edit'),
    # 文章编辑页里的图片上传功能
    path('news/images/', views.NewsUploadImage.as_view(), name='upload_image'),
    # 轮播图管理页
    path('banners/', views.BannerManageView.as_view(), name='banners_manage'),
    # 轮播图编辑功能
    path('banners_edit/<int:banner_id>/', views.BannerEditView.as_view(), name='banners_edit'),
    # 添加轮播图
    path('banners/add/', views.BannerAddView.as_view(), name='banners_add'),
    # 课程管理页
    path('courses/', views.CourseManageView.as_view(), name='course_manage'),
    # 课程编辑页
    path('courses/<int:course_id>/', views.CourseEditView.as_view(), name='course_edit'),
    # 课程创建页
    path('courses/pub/', views.CoursePubView.as_view(), name='course_pub'),
    # 文档管理页
    path('doc/', views.DocMangeView.as_view(), name='doc_manage'),
    # 文档更新
    path('docs/<int:doc_id>/', views.DocEditView.as_view(), name='doc_edit'),
    # 添加文档
    path('docs/pub/', views.DocsPubView.as_view(), name='docs_pub'),
    # 文档上传功能
    path('docs/files/', views.DocsUploadFile.as_view(), name='upload_text'),
    # 用户组管理页
    path('groups/', views.GroupsManageView.as_view(), name='groups_manage'),
    # 用户组编辑页
    path('groups/<int:group_id>/', views.GroupsEditView.as_view(), name='groups_edit'),
    # 用户组添加页
    path('groups/add/', views.GroupsAddView.as_view(), name='groups_add'),
]
