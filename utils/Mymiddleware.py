# 自定义中间件
from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin


class MyMiddleware(MiddlewareMixin):
    """
    自定义csrf中间件
    实现全局csrf,不用每个页面去添加
    """

    def process_request(self, request):
        get_token(request)
