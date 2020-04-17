from django.db import models


class ModelBase(models.Model):
    """
    设置模型类公共字段
    django会自动设定创建和修改字段的时间
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        abstract = True  # 设置为抽象模型类, 用于其他模型来继承，数据库迁移时不会创建ModelBase表
