from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='index'),
    path('detail<int:course_id>/', views.CourseDetail.as_view(), name='detail'),
    # 移动端接口
    path('videolist', views.video_list, name='videolist'),
    path('mobile', views.mobile_course_list),
    path('mobile2', views.mobile_course_list2),
]
