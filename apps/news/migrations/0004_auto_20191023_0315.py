# Generated by Django 2.1.7 on 2019-10-22 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_auto_20191022_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='priority',
            field=models.IntegerField(choices=[(1, '第一级'), (2, '第二级'), (3, '第三级'), (4, '第四级'), (5, '第五级'), (6, '第六级')], default=6, verbose_name='轮播图优先级'),
        ),
        migrations.AlterField(
            model_name='hotnews',
            name='priority',
            field=models.IntegerField(choices=[(1, '第一级'), (2, '第二级'), (3, '第三级')], verbose_name='热门新闻优先级'),
        ),
    ]