# 配置启动文件
from celery import Celery

# 为celery 使用django 进行配置

import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'my_news.settings'

# 创建实例
app = Celery('sms_code')

# 导入配置
app.config_from_object('celery_tasks.config')

# 自定义注册任务
app.autodiscover_tasks(['celery_tasks.sms'])
