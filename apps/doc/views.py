from django.shortcuts import render
from django.http import FileResponse, Http404
from django.utils.encoding import escape_uri_path
from django.views import View
from django.conf import settings
import requests

from .models import Doc

import logging
# 导入日志器
logger = logging.getLogger('django')


def doc_index(request):
    """
    """
    docs = Doc.objects.defer('author', 'create_time', 'update_time', 'is_delete').filter(is_delete=False)  # 排除不用的字段
    return render(request, 'doc/docDownload.html', locals())


class DocDownload(View):
    """
    """
    def get(self, request, doc_id):
        doc = Doc.objects.only('file_url').filter(is_delete=False, id=doc_id).first()
        if doc:
            doc_file_url = doc.file_url
            # 判断文件的路径格式,进行过滤是否添加域名
            doc_url = settings.SITE_DOMAIN_PORT + doc_file_url if doc_file_url.split('/')[0] == '' else doc_file_url

            # 流文件的处理
            try:
                res = FileResponse(requests.get(doc_url, stream=True))
                # 仅测试的话可以这样子设置
                # res = FileResponse(open(doc.file_url, 'rb'))
            except Exception as e:
                logger.info("获取文档内容出现异常：\n{}".format(e))
                raise Http404("文档下载异常！")

            # 关于FileResponse下载功能的详细介绍
            # https://stackoverflow.com/questions/23714383/what-are-all-the-possible-values-for-http-content-type-header
            # http://www.iana.org/assignments/media-types/media-types.xhtml#image

            # 获取文件后缀
            ex_name = doc_url.split('.')[-1]
            if not ex_name:
                raise Http404("文档url异常！")
            else:
                ex_name = ex_name.lower()  # 转换小写
            # 判断是什么格式的文件
            if ex_name == "pdf":
                res["Content-type"] = "application/pdf"
            elif ex_name == "zip":
                res["Content-type"] = "application/zip"
            elif ex_name == "doc":
                res["Content-type"] = "application/msword"
            elif ex_name == "xls":
                res["Content-type"] = "application/vnd.ms-excel"
            elif ex_name == "docx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ex_name == "ppt":
                res["Content-type"] = "application/vnd.ms-powerpoint"
            elif ex_name == "pptx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            else:
                raise Http404("文档格式不正确！")

            # http://192.168.216.137:8000/media/流畅的python.pdf >>> 流畅的python.pdf
            doc_filename = escape_uri_path(doc_url.split('/')[-1])  # escape_uri_path用于过滤文件名称中不能用于url的字符
            # 设置为inline，会直接打开
            # 设置下载文件的默认名字
            res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_filename)
            return res

        else:
            raise Http404("文档不存在！")