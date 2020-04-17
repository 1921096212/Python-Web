from datetime import datetime
import json
from urllib.parse import urlencode

from django.core.paginator import Paginator, EmptyPage
from django.http import Http404

from admin import paginator_script, forms
from my_news import settings
from utils.fastdfs.fdfs import FDFS_Client
from utils.res_code import to_json_data
from utils.res_code import Code, error_map
from collections import OrderedDict

from django.shortcuts import render
from django.views import View
from django.db.models import Count

from news import models
from courses import models as cre
from doc import models as doc_models
from admin.forms import CoursePubForm
from django.contrib.auth.models import Group, Permission
from user.models import Users

import logging

logger = logging.getLogger('django')


class IndexView(View):
    """
    后台主页面
    """

    def get(self, request):
        return render(request, 'admin/index/index.html')


class TagsManageView(View):
    """
    标签管理
    """

    @staticmethod
    def get(request):
        """
        """
        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')).filter(
            is_delete=False).order_by('-num_news')
        return render(request, 'admin/news/tags_manage.html', locals())

    @staticmethod
    def post(request):
        """
        添加标签
        """
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        tag_name = dict_data.get('name')
        if tag_name and tag_name.strip():  # 用strip过滤首尾的空白
            # get_or_create:有值返回False 不保存, 没有值返回True 创建
            tag_tuple = models.Tag.objects.get_or_create(name=tag_name)
            return to_json_data(errmsg="标签创建成功") if tag_tuple[-1] else to_json_data(errno=Code.DATAEXIST,
                                                                                    errmsg="标签名已存在")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="标签名为空")

    @staticmethod
    def put(request, tag_id):
        """
         修改标签
        """
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_str.decode('utf8'))
        tag_name = dict_data.get('name')
        # 根据id找到要修改的数据
        tag = models.Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            if tag_name and tag_name.strip():  # tag_name.strip() 不能把空格保存到数据库所以要过滤
                # 检查该数据在数据库里是否已存在
                if not models.Tag.objects.only('id').filter(name=tag_name).exists():
                    # 保存
                    tag.name = tag_name
                    tag.save(update_fields=['name'])  # 指定字段更新
                    return to_json_data(errmsg='标签更新成功')
                else:
                    return to_json_data(errno=Code.DATAEXIST, errmsg='标签名已存在')
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg='标签名为空')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要更新的标签不存在')

    @staticmethod
    def delete(request, tag_id):
        """
         删除标签
        """
        tag = models.Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            tag.delete()
            return to_json_data(errmsg="标签更新成功")
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg="需要删除的标签不存在")


class HotNewManageView(View):
    """
    热门新闻表的管理
    """

    def get(self, request):
        hot_news = models.HotNews.objects.select_related('news__tag').only('news_id', 'news__title', 'news__tag__name',
                                                                           'priority').filter(is_delete=False).order_by(
            'priority', '-news__clicks')[0:3]
        return render(request, 'admin/news/hot_news.html', locals())

    def put(self, request, hot_news_id):
        """
        修改热门新闻
        :param request:
        :param hot_news_id:
        :return:
        """
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        # 获取参数
        try:
            priority = int(dict_data.get('priority'))
            # 判断它是否在热门新闻列表里
            priority_list = [i for i, _ in models.HotNews.PRI_CHOICES]
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='优先级设置错误')
        except Exception as e:
            logger.info('热门文章优先级错误{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='优先级设置错误')
        hotnews = models.HotNews.objects.only('id').filter(is_delete=False, id=hot_news_id).first()
        if not hotnews:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要更新的文章不存在')
        # 判断优先级是否有修改
        if hotnews.priority == priority:
            return to_json_data(errno=Code.PARAMERR, errmsg='优先级未修改')
        # 保存
        hotnews.priority = priority
        hotnews.save(update_fields=['priority'])
        return to_json_data(errmsg="热门文章更新成功")

    def delete(self, request, hot_news_id):
        """
        删除热门新闻
        :param request:
        :param hot_news_id:
        :return:
        """
        hotnews = models.HotNews.objects.only('id').filter(is_delete=False, id=hot_news_id).first()
        if hotnews:
            hotnews.is_delete = True
            hotnews.save(update_fields=['is_delete'])
            return to_json_data(errmsg='热门文章删除成功')
        else:
            return to_json_data(errno=Code.DATAERR, errmsg='数据错误')


class HotNewsAddView(View):
    """
    添加热门新闻页
    route: /admin/hotnews/add/
    """

    def get(self, request):
        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')). \
            filter(is_delete=False).order_by('-num_news', 'update_time')
        # 优先级列表
        # priority_list = {K: v for k, v in models.HotNews.PRI_CHOICES}
        priority_dict = OrderedDict(models.HotNews.PRI_CHOICES)

        return render(request, 'admin/news/hot_news_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))  # 将json转化为dict

        try:
            news_id = int(dict_data.get('news_id'))
        except Exception as e:
            logger.info('前端传过来的文章id参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        if not models.News.objects.filter(id=news_id).exists():
            return to_json_data(errno=Code.PARAMERR, errmsg='文章不存在')

        try:
            priority = int(dict_data.get('priority'))
            # 列表推导式
            priority_list = [i for i, _ in models.HotNews.PRI_CHOICES]
            # 判断是不是在设定的优先级列表里
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='热门文章的优先级设置错误')
        except Exception as e:
            logger.info('热门文章优先级异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='热门文章的优先级设置错误')

        # get_or_create:如果news_id已经在表里则直接从数据库返回此数据,否则创建此news_id并返回
        hot_news_tuple = models.HotNews.objects.get_or_create(news_id=news_id)
        # get_or_create:会返回一个标志位这里不需要只取第一位的内容
        hot_news = hot_news_tuple[0]
        hot_news.priority = priority  # 修改优先级
        hot_news.save(update_fields=['priority'])
        return to_json_data(errmsg="热门文章创建成功")


class NewsByTagIdView(View):
    """
    route: /admin/tags/<int:tag_id>/news/
    根据前端标签得到新闻id
    """

    def get(self, request, tag_id):
        newses = models.News.objects.values('id', 'title').filter(is_delete=False, tag_id=tag_id)
        news_list = [i for i in newses]
        return to_json_data(data={
            'news': news_list
        })


# 文章管理页面
class NewsManageView(View):
    """
    文章筛选
    """

    def get(self, request):
        tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)
        newses = models.News.objects.only('id', 'title', 'author__username', 'tag__name', 'update_time'). \
            select_related('author', 'tag').filter(is_delete=False)

        # 通过时间进行过滤
        try:
            # 得到开始时间
            start_time = request.GET.get('start_time', '')
            start_time = datetime.strptime(start_time, '%Y/%m/%d') if start_time else ''
            # 得到结束时间
            end_time = request.GET.get('end_time', '')
            end_time = datetime.strptime(end_time, '%Y/%m/%d') if end_time else ''
        except Exception as e:
            logger.info("用户输入的时间有误：\n{}".format(e))
            start_time = end_time = ''
        if start_time and not end_time:
            newses = newses.filter(update_time__lte=start_time)
        if end_time and not start_time:
            newses = newses.filter(update_time__gte=end_time)
        if start_time and end_time:
            newses = newses.filter(update_time__range=(start_time, end_time))

        # 通过title进行过滤
        title = request.GET.get('title', '')
        if title:
            newses = newses.filter(title__icontains=title)

        # 通过作者名进行过滤
        author_name = request.GET.get('author_name', '')
        if author_name:
            newses = newses.filter(author__username__icontains=author_name)

        # 通过标签id进行过滤
        try:
            tag_id = int(request.GET.get('tag_id', 0))
        except Exception as e:
            logger.info("标签错误：\n{}".format(e))
            tag_id = 0
        newses = newses.filter(is_delete=False, tag_id=tag_id) or newses.filter(is_delete=False)

        # 获取第几页内容
        try:
            page = int(request.GET.get('page', 1))  # 没取到数据设置默认第1页
        except Exception as e:
            logger.info("当前页数错误：\n{}".format(e))
            page = 1
        from . import constants
        paginator = Paginator(newses, constants.PER_PAGE_NEWS_COUNT)  # 一页显示多少个
        try:
            news_info = paginator.page(page)
        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logging.info("用户访问的页数大于总页数。")
            news_info = paginator.page(paginator.num_pages)  # 跳到最后一页

        # TODO: 自定义分页对象
        # 自定义分页对象
        paginator_data = paginator_script.get_paginator_data(paginator, news_info)

        start_time = start_time.strftime('%Y/%m/%d') if start_time else ''
        end_time = end_time.strftime('%Y/%m/%d') if end_time else ''
        context = {
            'news_info': news_info,
            'tags': tags,
            'paginator': paginator,
            'start_time': start_time,
            "end_time": end_time,
            "title": title,
            "author_name": author_name,
            "tag_id": tag_id,
            "other_param": urlencode({
                "start_time": start_time,
                "end_time": end_time,
                "title": title,
                "author_name": author_name,
                "tag_id": tag_id,
            })
        }
        context.update(paginator_data)
        return render(request, 'admin/news/news_manage.html', context=context)


# 文章编辑功能和页面
class NewsEditView(View):

    def get(self, request, news_id):
        """
        编辑文章的页面展示
        :param request:
        :param news_id:
        :return:
        """
        # 通过过滤id,得到需要的文章内容
        news = models.News.objects.filter(is_delete=False, id=news_id).first()
        if news:
            # 查出所有的分类标签
            tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)
            context = {
                "news": news,
                "tags": tags
            }
            return render(request, 'admin/news/news_pub.html', context=context)
        else:
            # 如果找不到那篇文章
            raise Http404('需要更新的文章不存在')

    def delete(self, request, news_id):
        """
        删除文章
        :param request:
        :param news_id:
        :return:
        """
        news = models.News.objects.only('id').filter(id=news_id).first()
        if news:
            # 把文章的逻辑删除is_delete字段设置为真
            news.is_delete = True
            # 保存到数据库
            news.save(update_fields=['is_delete'])
            return to_json_data(errmsg='文章删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要删除的文章不存在')

    def put(self, request, news_id):
        """
        更新文章
        :param request:
        :param news_id:
        :return:
        """
        # 得到数据库里的文章对象
        news = models.News.objects.only('id').filter(id=news_id).first()
        if not news:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的文章不存在')
        # 得到前端输入框里填的内容
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        # 表单验证前端的数据
        form = forms.NewsPubForm(data=dict_data)
        # 判断表单验证是否成功,is_valid:会返回表单验证后的状态
        if form.is_valid():
            # 如果验证没问题将各项数据写入数据库
            news.title = form.cleaned_data.get('title')
            news.digest = form.cleaned_data.get('digest')
            news.content = form.cleaned_data.get('content')
            news.image_url = form.cleaned_data.get('image_url')
            news.tag = form.cleaned_data.get('tag')
            news.save()
            return to_json_data(errmsg='文章更新成功')
        else:
            # 自定义表单校验错误后把错误各项返回给前端的方法
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 添加文章
class NewsAddView(View):
    def get(self, request):
        tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)
        context = {
            "tags": tags
        }
        return render(request, 'admin/news/news_pub.html', context=context)

    def post(self, request):
        # 得到前端输入框里填的内容
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        # 表单验证前端的数据
        form = forms.NewsPubForm(data=dict_data)
        # 判断表单验证是否成功,is_valid:会返回表单验证后的状态
        if form.is_valid():
            # TODO: 往表里添加数据的方法(文章)
            news = form.save(commit=False)
            # 如果验证没问题将各项数据写入数据库
            news.save()
            return to_json_data(errmsg='文章添加成功')
        else:
            # 自定义表单校验错误后把错误各项返回给前端的方法
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 图片上传至FastDFS服务器功能实现
# @method_decorator(csrf_exempt, name='dispatch')
class NewsUploadImage(View):
    def post(self, request):
        # 得到前端传的文件
        image_file = request.FILES.get('image_file')  # 2018.png
        if not image_file:
            logger.info('获取图片失败')
            return to_json_data(errno=Code.NODATA, errmsg='获取图片失败')
        # 检查图片类型
        if image_file.content_type not in ('image/jpeg', 'image/png', 'image/gif'):
            return to_json_data(errno=Code.DATAERR, errmsg='不能上传非图片文件')
        # 切割名字取图片格式
        try:
            image_ext_name = image_file.name.split('.')[-1]
        except Exception as e:
            logger.info('图片后缀名异常：{}'.format(e))
            image_ext_name = 'jpg'
        # 上传图片
        try:
            upload_res = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
        except Exception as e:
            logger.error('图片上传异常{}'.format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg='图片上传异常')
        else:
            # 判断返回的状态码,是否上传成功
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('图片上传到fdfs失败')
                return to_json_data(errno=Code.UNKOWNERR, errmsg='图片上传失败')
            else:
                # 得到上传成功文件的访问路径
                image_name = upload_res.get('Remote file_id')
                image_url = settings.FASTDFS_SERVER_DOMAIN + image_name
                # 将路径返回到前端
                return to_json_data(data={'image_url': image_url}, errmsg='图片上传成功')


# 轮播图管理页面
class BannerManageView(View):

    def get(self, request):
        # 排序
        priority_dict = OrderedDict(models.Banner.PRI_CHOICES)
        # 取到数据
        banners = models.Banner.objects.only('id', 'image_url', 'priority').filter(is_delete=False)
        return render(request, 'admin/news/news_banner.html', locals())


# 轮播图编辑功能
class BannerEditView(View):

    def delete(self, request, banner_id):
        banner = models.Banner.objects.only('id').filter(id=banner_id).first()
        if banner:
            # 用逻辑删除
            banner.is_delete = True
            banner.save(update_fields=['is_delete'])
            return to_json_data(errmsg='轮播图删除成功！')
        else:
            return to_json_data(errno=Code.NODATA, errmsg='轮播图不存在')

    def put(self, request, banner_id):
        banner = models.Banner.objects.only('id').filter(id=banner_id, is_delete=False).first()
        if not banner:
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图不存在')
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))

        try:
            # 取到前端的优先级值
            priority = int(dict_data['priority'])
            # 取到模型类里的数据
            priority_list = [i for i, _ in models.Banner.PRI_CHOICES]
            # 判断前端传的轮播图优先级数据有没有在数据库里
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='轮播图优先级设置错误')
        except Exception as e:
            logger.info('轮播图优先级异常\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图优先级设置错误')
        # 取到前端图片url
        image_url = dict_data['image_url']
        if not image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg='图片为空')
        # 和后台比较有没有改变
        if banner.priority == priority and banner.image_url == image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图优先级未更改')
        # 保存到数据库
        banner.priority = priority
        banner.image_url = image_url
        banner.save(update_fields=['priority', 'image_url'])
        return to_json_data(errmsg='轮播图更新成功')


# 添加轮播图页
class BannerAddView(View):

    def get(self, request):
        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')). \
            filter(is_delete=False).order_by('-num_news', 'update_time')
        # 优先级列表
        # priority_list = {K: v for k, v in models.Banner.PRI_CHOICES}
        priority_dict = OrderedDict(models.Banner.PRI_CHOICES)

        return render(request, 'admin/news/news_banner_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        try:
            news_id = int(dict_data.get('news_id'))
        except Exception as e:
            logger.info('前端传过来的文章id参数异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        if not models.News.objects.filter(id=news_id).exists():
            return to_json_data(errno=Code.PARAMERR, errmsg='文章不存在')

        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in models.Banner.PRI_CHOICES]
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='轮播图的优先级设置错误')
        except Exception as e:
            logger.info('轮播图优先级异常：\n{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图的优先级设置错误')

        # 获取轮播图url
        image_url = dict_data.get('image_url')
        if not image_url:
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图url为空')

        # 创建轮播图
        banners_tuple = models.Banner.objects.get_or_create(news_id=news_id)
        banner, is_created = banners_tuple

        banner.priority = priority
        banner.image_url = image_url
        banner.save(update_fields=['priority', 'image_url'])
        return to_json_data(errmsg="轮播图创建成功")


# 课程管理页
class CourseManageView(View):
    def get(self, request):
        courses = cre.Course.objects.select_related('category', 'teacher'). \
            only('title', 'category__name', 'teacher__name').filter(is_delete=False)
        return render(request, 'admin/course/course_manage.html', locals())


# 课程编辑页
class CourseEditView(View):
    def get(self, request, course_id):
        course = cre.Course.objects.filter(is_delete=False, id=course_id).first()
        if course:
            # 教师表
            teachers = cre.Teacher.objects.only('name').filter(is_delete=False)
            # 课程分类表
            categories = cre.CourseCategory.objects.only('name').filter(is_delete=False)
            return render(request, 'admin/course/news_pub.html', locals())
        else:
            Http404('需要更新的课程不存在')

    def delete(self, request, course_id):
        course = cre.Course.objects.only('id').filter(is_delete=False, id=course_id).first()
        if course:
            course.is_delete = True
            course.save(update_fields=['is_delete'])
            return to_json_data(errmsg='课程删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='更新的课程不存在')

    def put(self, request, course_id):
        course = cre.Course.objects.filter(is_delete=False, id=course_id).first()
        if not course:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的课程不存在')
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_str.decode('utf8'))
        # 表单验证
        form = CoursePubForm(data=dict_data)
        if form.is_valid():
            # 循环将所有字段保存到数据库
            for attr, value in form.cleaned_data.items():
                setattr(course, attr, value)
            course.save()
            return to_json_data(errmsg='课程更新成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 课程创建页
class CoursePubView(View):
    def get(self, request):
        teachers = cre.Teacher.objects.only('name').filter(is_delete=False)
        categories = cre.CourseCategory.objects.only('name').filter(is_delete=False)
        return render(request, 'admin/course/news_pub.html', locals())

    def post(self, request):
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        data_dict = json.loads(json_str.decode('utf8'))
        form = forms.CoursePubForm(data=data_dict)
        if form.is_valid():
            # TODO: 往表里添加数据的方法(课程)
            # commit=False:不直接保存,返回一个对象,单独保存
            course_instance = form.save(commit=False)
            course_instance.save()
            return to_json_data(errmsg='课程发布成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 文档管理页
class DocMangeView(View):
    def get(self, request):
        docs = doc_models.Doc.objects.only('title', 'create_time').filter(is_delete=False)
        return render(request, 'admin/doc/docs_manage.html', locals())


# 文档编辑
class DocEditView(View):

    def get(self, request, doc_id):
        doc = doc_models.Doc.objects.only('id').filter(id=doc_id).first()
        if doc:
            return render(request, 'admin/doc/doc_pub.html', locals())
        else:
            raise Http404('需要更新得文档不存在')

    def delete(self, request, doc_id):
        doc = doc_models.Doc.objects.only('id').filter(id=doc_id).first()
        if doc:
            doc.is_delete = True
            doc.save(update_fields=['is_delete'])
            return to_json_data(errmsg='文档删除成功')
        else:
            to_json_data(errno=Code.PARAMERR, errmsg='需要删除的文档不存在')

    # 更新文档
    def put(self, request, doc_id):
        doc = doc_models.Doc.objects.only('id').filter(id=doc_id).first()
        if not doc:
            return to_json_data(errno=Code.NODATA, errmsg='需要更新的文档不存在')
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.DocsPubForm(data=dict_data)
        if form.is_valid():
            doc.title = form.cleaned_data.get('title')
            doc.desc = form.cleaned_data.get('desc')
            doc.file_url = form.cleaned_data.get('file_url')
            doc.image_url = form.cleaned_data.get('image_url')
            doc.save()
            return to_json_data(errmsg='文档更新成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 文档上传功能
class DocsUploadFile(View):
    """route: /admin/doc/files/
    """

    def post(self, request):
        text_file = request.FILES.get('text_file')
        if not text_file:
            logger.info('从前端获取文件失败')
            return to_json_data(errno=Code.NODATA, errmsg='从前端获取文件失败')

        if text_file.content_type not in (
                'application/octet-stream', 'application/pdf', 'application/zip', 'text/plain', 'application/x-rar'):
            return to_json_data(errno=Code.DATAERR, errmsg='不能上传非文本文件')

        try:
            text_ext_name = text_file.name.split('.')[-1]
        except Exception as e:
            logger.info('文件拓展名异常：{}'.format(e))
            text_ext_name = 'pdf'

        try:
            x = text_file.read()
            upload_res = FDFS_Client.upload_by_buffer(x, file_ext_name=text_ext_name)
            # upload_res = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
        except Exception as e:
            logger.error('文件上传出现异常：{}'.format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg='文件上传异常')
        else:
            if upload_res.get('Status') != 'Upload successed.':
                logger.info('文件上传到FastDFS服务器失败')
                return to_json_data(Code.UNKOWNERR, errmsg='文件上传到服务器失败')
            else:
                text_name = upload_res.get('Remote file_id')
                text_url = settings.FASTDFS_SERVER_DOMAIN + text_name
                return to_json_data(data={'text_file': text_url}, errmsg='文件上传成功')


# 创建文档页
class DocsPubView(View):
    """
    route: /admin/news/pub/
    """

    def get(self, request):
        return render(request, 'admin/doc/doc_pub.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        # 将json转化为dict
        dict_data = json.loads(json_data.decode('utf8'))

        form = forms.DocsPubForm(data=dict_data)
        if form.is_valid():
            # TODO: 往表里添加数据的方法(文档)
            docs_instance = form.save(commit=False)
            # 修改save返回的对象的一个值
            docs_instance.author_id = request.user.id
            docs_instance.save()
            return to_json_data(errmsg='文档创建成功')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 用户组管理页
class GroupsManageView(View):
    """
    route: /admin/groups/
    """

    def get(self, request):
        groups = Group.objects.values('id', 'name').annotate(num_users=Count('user')).order_by('-num_users', 'id')
        return render(request, 'admin/user/groups_manage.html', locals())


# 用户组编辑页
class GroupsEditView(View):

    def get(self, request, group_id):
        group = Group.objects.filter(id=group_id).first()
        if group:
            permission = Permission.objects.only('id').all()  # 取到所有权限
            return render(request, 'admin/user/groups_add.html', locals())
        else:
            raise Http404('编辑的用户组不存在')

    def put(self, request, group_id):
        group = Group.objects.filter(id=group_id).first()
        # 判断数据库是否有该权限组
        if not group:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        json_str = request.body
        # 空参数过滤
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        dict_data = json.loads(json_str)
        # 空组名过滤
        group_name = dict_data.get('name', '').strip()
        if not group_name:
            return to_json_data(errno=Code.PARAMERR, errmsg='组名为空')
        # 判断是否已存在该组名
        if group_name != group.name and Group.objects.filter(name=group_name).exists():
            return to_json_data(errno=Code.DATAEXIST, errmsg='组名已存在')
        # 得到前端传的权限组
        group_permissions = dict_data.get('group_permissions')  # [1,2,3,4,5,6,7,8]
        # 空权限组过滤
        if not group_permissions:
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数为空')
        # 转集合去重
        permissions_set = set(int(i) for i in group_permissions)
        db_permissions_set = set(i.id for i in group.permissions.all())
        # 如果和数据库里的完全相同
        if group_name == group.name and permissions_set == db_permissions_set:
            return to_json_data(errno=Code.DATAEXIST, errmsg='用户组没有修改')
        # 保存权限
        for i in permissions_set:
            p = Permission.objects.get(id=i)
            group.permissions.add(p)
        # 保存组名
        group.name = group_name
        group.save()
        return to_json_data(errmsg='组更新成功')

    def delete(self, request, group_id):
        group = Group.objects.filter(id=group_id).first()
        if group:
            group.permissions.clear()  # 清空权限
            group.delete()
            return to_json_data(errmsg='删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要删除的用户组不存在')


# 用户组添加页
class GroupsAddView(View):
    """
    route: admin/groups/add/
    """

    def get(self, request):
        permission = Permission.objects.only('id').all()
        return render(request, 'admin/user/groups_add.html', context={'permission': permission})

    def post(self, request):
        """
        1, 获取表单的数据
        数据清洗
        2， 获取参数进行
        组名 判断数据库里面是否有值  组权限
        3， 保存 返回
        :return:
        """
        group = Group.objects.filter()
        # 判断数据库是否有该权限组
        # if not group:
        #     return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        json_str = request.body
        # 空参数过滤
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        dict_data = json.loads(json_str)
        # 空组名过滤
        group_name = dict_data.get('name', '').strip()
        if not group_name:
            return to_json_data(errno=Code.PARAMERR, errmsg='组名为空')
        # 判断是否已存在该组名
        if Group.objects.filter(name=group_name).exists():
            return to_json_data(errno=Code.DATAEXIST, errmsg='组名已存在')
        # 得到前端传的权限组
        group_permissions = dict_data.get('group_permissions')  # [1,2,3,4,5,6,7,8]
        # 空权限组过滤
        if not group_permissions:
            return to_json_data(errno=Code.PARAMERR, errmsg='权限参数为空')
        # 转集合去重
        permissions_set = set(int(i) for i in group_permissions)
        # db_permissions_set = set(i.id for i in group.permissions.all())
        # # 如果和数据库里的完全相同
        # if group_name == group.name and permissions_set == db_permissions_set:
        #     return to_json_data(errno=Code.DATAEXIST, errmsg='用户组没有修改')
        # 保存权限
        # obj = models.Tb1(c1='xx', c2='oo')
        # obj.save()

        for i in permissions_set:
            p = Permission.objects.get(id=i)
            # Group.objects.create(id=p)
            # print(p)
            group.permissions.add(p)
        # # 保存组名
        group.name = group_name
        group.save()
        # Group.objects.create(name=group_name)
        return to_json_data(errmsg='组更新成功')


# 用户权限
class UserManageView(View):
    def get(self, request):
        users = Users.objects.only('is_staff', 'is_superuser', 'username').filter(is_active=True)

        return render(request, 'admin/user/user_manage.html', locals())


class UserEditView(View):
    def get(self, request, user_id):
        user_instance = Users.objects.filter(id=user_id).first()
        if user_instance:
            groups = Group.objects.only('name').all()
            return render(request, 'admin/user/user_edit.html', locals())
        else:
            raise Http404('更新得用户组不存在')

    def put(self, request, user_id):
        user_instance = Users.objects.filter(id=user_id).first()
        if not user_instance:
            return to_json_data(errno=Code.NODATA, errmsg='无数据')

        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.NODATA])

        dict_data = json.loads(json_str)
        try:
            groups = dict_data.get('groups')
            is_superuser = int(dict_data['is_superuser'])  # 0
            is_staff = int(dict_data.get('is_staff'))  # 1
            is_active = int(dict_data['is_active'])  # 1
            params = (is_active, is_staff, is_superuser)
            if not all([q in (0, 1) for q in params]):
                return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        except Exception as e:
            logger.info('从前端获取得用户参数错误{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        try:
            if groups:
                groups_set = set(int(i) for i in groups)
            else:
                groups_set = set()
        except Exception as e:
            logger.info('用户组参数异常{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='用户组参数异常')

        # 组
        all_groups_set = set(i.id for i in Group.objects.only('id'))
        # 判断前台传得组是否在所有用户组里面
        if not groups_set.issubset(all_groups_set):
            return to_json_data(errno=Code.PARAMERR, errmsg='有不存在的用户组参数')

        gsa = Group.objects.filter(id__in=groups_set)  # [1,3,4]

        # 保存
        user_instance.groups.clear()
        user_instance.groups.set(gsa)
        user_instance.is_staff = bool(is_staff)
        user_instance.is_superuser = bool(is_superuser)
        user_instance.is_active = bool(is_active)
        user_instance.save()
        return to_json_data(errmsg='用户组更新成功')

    def delete(self, request, user_id):
        user_instance = Users.objects.filter(id=user_id).first()
        if user_instance:
            user_instance.groups.clear()  # 去除用户组
            user_instance.user_permissions.clear()  # 清楚用户权限
            user_instance.is_active = False
            user_instance.save()
            return to_json_data(errmsg='用户删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='需要删除的用户不存在')
