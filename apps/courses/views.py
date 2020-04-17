from django.shortcuts import render
from django.views import View
from django.http import Http404, JsonResponse, HttpResponse

from utils.res_code import to_json_data
from . import models
import logging

# 导入日志器
logger = logging.getLogger('django')


# 课程目录
def course_list(request):
    courses = models.Course.objects.only('title', 'cover_url', 'teacher__name').filter(is_delete=False)
    return render(request, 'course/course.html', locals())


# 课程详情
class CourseDetail(View):
    def get(self, request, course_id):
        try:
            course = models.Course.objects.only('title', 'cover_url', 'video_url', 'profile', 'outline',
                                                'teacher__name', 'teacher__positional_title',
                                                'teacher__avatar_url', 'teacher__profile').select_related(
                'teacher').filter(is_delete=False, id=course_id).first()
        except models.Course.DoesNotExist as e:
            logger.info('当前课程出现异常{}'.format(e))
            raise Http404('课程不存在')
        return render(request, 'course/course_detail.html', locals())


# ----------------------------移动端接口----------------------------
# 视频列表
def video_list(request):
    courses = models.Course.objects.only('title', 'cover_url', 'profile').filter(is_delete=False, teacher__name='心蓝')
    return render(request, 'mobile/videolist.html', locals())


# 视频api
def mobile_course_list(request):
    courses = models.Course.objects.only('title', 'cover_url', 'video_url').filter(is_delete=False, teacher__name='心蓝')
    data = []
    for i in courses:
        context = {}
        # context.setdefault('id', i.id)
        context.setdefault('title', i.title)
        context.setdefault('cover_url', i.cover_url)
        context.setdefault('video_url', i.video_url)
        data.append(context)
    return to_json_data(data=data)


def mobile_course_list2(request):
    data = []
    context = {}
    context.setdefault('title', '辛弃疾1162')
    context.setdefault('video_url', 'http://jx.drgxj.com/?url=https://www.iqiyi.com/v_19rwfzgz7w.html')
    data.append(context)
    context = {}
    context.setdefault('title', '中国机长')
    context.setdefault('video_url', 'http://www.vipjiexi.com/yun.php?url=https%3A%2F%2Fwww.iqiyi.com%2Fv_19rsho7kz8.html%3Fvfrm%3Dpcw_home%26vfrmblk%3DC%26vfrmrst%3D711219_home_channel_dianying_pic2')
    data.append(context)
    context = {}
    context.setdefault('title', '你是凶手')
    context.setdefault('video_url', 'http://www.vipjiexi.com/yun.php?url=https%3A%2F%2Fwww.iqiyi.com%2Fv_19ru1uo134.html%3Fvfrm%3Dpcw_home%26vfrmblk%3DC%26vfrmrst%3D711219_home_channel_dianying_pic3')
    data.append(context)
    context = {}
    context.setdefault('title', '双子杀手')
    context.setdefault('video_url', 'http://www.vipjiexi.com/yun.php?url=https%3A%2F%2Fwww.iqiyi.com%2Fv_19rrcb0s44.html%3Fvfrm%3Dpcw_home%26vfrmblk%3DC%26vfrmrst%3D711219_home_channel_dianying_pic4')
    data.append(context)

    return to_json_data(data=data)
