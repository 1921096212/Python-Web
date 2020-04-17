from django.db import models
from utils.BaseModel import ModelBase

"""
1.分析
- 文章分类表： name     create_time  update_time   is_delete
- 文章表： title  digest  content   clicks   image_url    author(一对对多)   tag(一对多关系)
- 文章评论表：content   author(一对多关系)   news()
- 热门文章表：news(一对一)   pirority
- 轮播图表： image_url   pirority    news(一对一)
"""


# 新闻标签
class Tag(ModelBase):
    name = models.CharField(max_length=64, verbose_name='标签名', help_text='标签名')

    # 建表排序
    class Meta:
        ordering = ['-update_time', '-id']  # 加-号逆序排序,从大到小
        db_table = 'tb_tag'  # 表名
        verbose_name = '新闻标签'  # 在admin站点中显示的名称
        # verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.name


# 新闻表
class News(ModelBase):
    title = models.CharField(max_length=150, verbose_name='标题', help_text='标签')
    digest = models.CharField(max_length=200, verbose_name='摘要')
    content = models.TextField(verbose_name='内容')
    clicks = models.IntegerField(default=0, verbose_name='点击量')
    image_url = models.URLField(default='', verbose_name='图片')
    tag = models.ForeignKey('Tag', on_delete=models.SET_NULL, null=True)  # 与Tag表关联,SET_NULL,null=True新闻被删除被关联的表不会改变,一对多
    author = models.ForeignKey('user.Users', on_delete=models.SET_NULL, null=True)  # 与用户表关联,一对多

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_news'
        verbose_name = '新闻'

    def __str__(self):
        return self.title


# 新闻内容加评论
class Comments(ModelBase):
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey('user.Users', on_delete=models.SET_NULL, null=True)
    news = models.ForeignKey('News', on_delete=models.CASCADE)  # 级联删除,新闻被删除,评论也被删除
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)  # 父评论删除子评论也删除,null:可以为空,blank:可以为空白

    def to_dict_data(self):
        comment_dict = {
            'news_id': self.news.id,
            'content_id': self.id,
            'content': self.content,
            'author': self.author.username,
            'update_time': self.update_time.strftime('%Y年%m月%d日 %H:%M'),
            'parent': self.parent.to_dict_data() if self.parent else None,
        }
        return comment_dict

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_comment'
        verbose_name = '评论'

    def __str__(self):
        return '评论{}'.format(self.id)


# 热门新闻
class HotNews(ModelBase):
    # 设置优先级
    PRI_CHOICES = [
        (1, '第一级'),
        (2, '第二级'),
        (3, '第三级'),
    ]
    news = models.OneToOneField('News', on_delete=models.CASCADE)  # 级联删除,一对一关系
    priority = models.IntegerField(choices=PRI_CHOICES, verbose_name='热门新闻优先级')  # 热门新闻的顺序

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_hot'
        verbose_name = '热门新闻'

    def __str__(self):
        return '热门新闻{}'.format(self.id)


# 轮播图
class Banner(ModelBase):
    PRI_CHOICES = [
        (1, '第一级'),
        (2, '第二级'),
        (3, '第三级'),
        (4, '第四级'),
        (5, '第五级'),
        (6, '第六级'),
    ]
    image_url = models.URLField(verbose_name='轮播图url')
    priority = models.IntegerField(choices=PRI_CHOICES, default=6, verbose_name='轮播图优先级')  # 轮播图的顺序
    news = models.OneToOneField('News', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_banner'
        verbose_name = '轮播图'

    def __str__(self):
        return '轮播图{}'.format(self.id)
