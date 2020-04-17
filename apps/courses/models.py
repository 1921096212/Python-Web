from utils.BaseModel import ModelBase
from django.db import models


# Create your models here.


# 教师
class Teacher(ModelBase):
    name = models.CharField(max_length=50, verbose_name='讲师姓名')
    positional_title = models.CharField(max_length=150, verbose_name='职称')
    profile = models.TextField(verbose_name='讲师简介')
    avatar_url = models.URLField(verbose_name='头像url', default='')

    class Meta:
        db_table = 'tb_teachers'
        verbose_name = '讲师'

    def __str__(self):
        return self.name


# 课程分类
class CourseCategory(ModelBase):
    """
    娱乐  搞笑   学习  python c++  java
    """
    name = models.CharField(max_length=80, verbose_name='课程分类')

    class Meta:
        db_table = 'tb_course_category'
        verbose_name = '课程分类'

    def __str__(self):
        return self.name


# 课程详情
class Course(ModelBase):
    title = models.CharField(max_length=80, verbose_name='课程名字')
    cover_url = models.URLField(verbose_name='课程封面url')
    video_url = models.URLField(verbose_name='视频url')
    duration = models.FloatField(default=0.0, verbose_name='视频时长')
    profile = models.TextField(null=True, blank=True, verbose_name='课程简介')
    outline = models.TextField(null=True, blank=True, verbose_name='课程大纲')

    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=
    True, blank=True)

    class Meta:
        db_table = 'tb_course'
        verbose_name = '课程详情'

    def __str__(self):
        return self.title
