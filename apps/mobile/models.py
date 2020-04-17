from django.db import models
from utils.BaseModel import ModelBase

# Create your models here.


# 瀑布图片表
class FlowImage(ModelBase):
    title = models.CharField(max_length=150, verbose_name='标题')
    image_url = models.URLField(verbose_name='图片')

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_mobile_flowImageUrl'

    def __str__(self):
        return self.title
