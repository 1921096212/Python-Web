from django.db import models

from utils.BaseModel import ModelBase


class Doc(ModelBase):
    file_url = models.URLField(verbose_name='文件url', help_text='文件url')
    title = models.CharField(max_length=150, verbose_name='文档标题')
    desc = models.TextField(verbose_name='文档描述')
    image_url = models.URLField(default='', verbose_name='图片url')
    author = models.ForeignKey('user.Users', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'tb_docs'
        verbose_name = '文档'

    def __str__(self):
        return self.title
