import json

from django.db.models import F
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
from . import models
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from utils.res_code import to_json_data, Code, error_map
from haystack.views import SearchView as _Search
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

import logging

logger = logging.getLogger('django')


# 主页面
# @method_decorator(cache_page(timeout=120, cache='page_cache'), name='dispatch')  # 把页面加到redis缓存
class IndexView(View):
    def get(self, request):
        # 分类新闻
        tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)  # only得到指定字段的数据,filter过滤器
        # 获取热门新闻
        hot_news = models.HotNews.objects.select_related('news').only('news__title', 'news__image_url',
                                                                      'news_id').filter(is_delete=False).order_by(
            'priority', '-news__clicks')[0:3]

        return render(request, 'news/index.html', locals())  # locals把定义的所有局部变量通过字典方式返回渲染到前台


# 新闻列表数据
class NewsListView(View):
    def get(self, request):
        """
        参数
        tag_id
        page
        route:/news/
        :param request:
        :return:
        """
        # 获取前台的参数 http://127.0,0,1:8000/?tag_id=0&page=1
        # 因为转换int可能报错需要try
        try:
            tag_id = int(request.GET.get('tag_id', 0))  # 默认为0
        except Exception as e:
            logger.error('标签错误\n{}'.format(e))
            tag_id = 0
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.error('页面错误\n{}'.format(e))
            page = 1

        # 查询及对象
        # news_list = models.News.objects.select_related('tag', 'author').only(
        #     'id', 'image_url', 'title', 'digest', 'author__username', 'tag__name', 'update_time'
        # ).filter(is_delete=False)

        # TODO :查询方法重点区域
        # values返回为字典类型
        # F另取一个关联字段的名字
        news_list = models.News.objects.values('id', 'title', 'image_url', 'digest', 'update_time').annotate(
            tag_name=F('tag__name'), author=F('author__username'))
        # 如果获取的标签不正确,则默认返回全部新闻
        news = news_list.filter(is_delete=False, tag_id=tag_id) or news_list.filter(is_delete=False)  # 对比,与前后台tag_id对应

        # 分页功能
        paginator = Paginator(news, 5)
        try:
            # 也可以用get_page(),自带容错
            news_info = paginator.page(page)
        except Exception as e:
            logger.info('给定的页码错误{}'.format(e))
            news_info = Paginator.page(paginator.num_pages)

        # news_info_list = []
        # for n in news_info:
        #     news_info_list.append({
        #         'id': n.id,
        #         'title': n.title,
        #         'digest': n.digest,
        #         'author': n.author.username,
        #         'image_url': n.image_url,
        #         'tag_name': n.tag.name,
        #         'update_time': n.update_time
        #     })

        data = {
            'news': list(news_info),
            'total_pages': paginator.num_pages
        }
        return to_json_data(data=data)


# 新闻详情
@method_decorator(cache_page(timeout=120, cache='page_cache'), name='dispatch')
class NewsDetail(View):
    def get(self, request, news_id):
        # 获取新闻内容
        news = models.News.objects.select_related('tag', 'author').only('title', 'content', 'update_time', 'tag__name',
                                                                        'author__username').filter(is_delete=False,
                                                                                                   id=news_id).first()
        # 获取新闻评论
        comments = models.Comments.objects.select_related('author', 'parent').only('author__username', 'update_time',
                                                                                   'parent__author__username',
                                                                                   'content').filter(
            is_delete=False, news_id=news_id)
        comments_list = []
        for comm in comments:
            comments_list.append(comm.to_dict_data())

        if news:
            return render(request, 'news/news_detail.html', locals())
        else:
            return HttpResponseNotFound('PAGE NOT FOUND')  # 访问的页面不存在


# 轮播图
class BannerView(View):
    def get(self, request):
        # banners = models.Banner.objects.select_related('news').only('image_url', 'news__title', 'news_id').filter(
        #     is_delete=False)[0:6]
        banners = models.Banner.objects.values('image_url').annotate(news_id=F('news_id'),
                                                                     news_title=F('news__title')).filter(
            is_delete=False)[0:6]
        # banner_info = []
        # for i in banners:
        #     banner_info.append({
        #         'image_url': i.image_url,
        #         'news_id': i.news.id,  # ID 传给前台做轮播图详情页渲染
        #         'news_title': i.news.title
        #     })
        data = {
            'banners': list(banners)
        }

        return to_json_data(data=data)


# 新闻评论
class CommentView(View):
    def post(self, request, news_id):
        if not request.user.is_authenticated:  # 用户未登录
            return to_json_data(errno=Code.SESSIONERR, errmsg=error_map[Code.SESSIONERR])
        if not models.News.objects.only('id').filter(is_delete=False, id=news_id).exists():  # 新闻不存在
            return to_json_data(errno=Code.PARAMERR, errmsg='新闻不存在')
        # 获取参数
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        dict_data = json.loads(json_str)
        # 一级评论
        content = dict_data.get('content')
        if not dict_data.get('content'):
            return to_json_data(errno=Code.PARAMERR, errmsg='评论数据不能为空')
        # 回复评论 二级评论
        pt_id = dict_data.get('parent_id')
        try:
            if pt_id:
                if not models.Comments.objects.only('id').filter(is_delete=False, id=pt_id, news_id=news_id).exists():
                    return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        except Exception as e:
            logging.info('前台传的parent_id异常{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='未知异常')

        # 保存到数据库
        news_content = models.Comments()
        news_content.content = content
        news_content.news_id = news_id
        news_content.author = request.user
        news_content.parent_id = pt_id if pt_id else None
        news_content.save()
        # 序列化返回
        return to_json_data(data=news_content.to_dict_data())


# 快速搜索
class Search(_Search):
    template = 'news/search.html'

    def create_response(self):
        # 获取前端数据 通过键拿到值
        kw = self.request.GET.get('q', '')
        # 如果搜索框没有内容则返回热门推荐的数据
        if not kw:
            show = True
            hot_news = models.HotNews.objects.select_related('news').only('news__title', 'news__image_url',
                                                                          'news__id').filter(
                is_delete=False).order_by('priority', '-news__clicks')
            # 参数 分页
            paginator = Paginator(hot_news, 5)
            try:
                # 假如不是整数
                page = paginator.page(int(self.request.GET.get('page', 1)))
            except PageNotAnInteger:
                # 默认返回第一页
                page = paginator.page(1)
            except EmptyPage:
                page = paginator.page(paginator.num_pages)
            return render(self.request, self.template, locals())
        else:
            # 如果有值
            show = False
            return super().create_response()
