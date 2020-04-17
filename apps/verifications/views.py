import random

from django.shortcuts import render
from django_redis import get_redis_connection
from django.views import View
from django.http import HttpResponse, JsonResponse

from utils.captcha.captcha import captcha
from utils.res_code import to_json_data, error_map, Code
from user.models import Users

from utils.yuntongxun.sms import CCP
from celery_tasks.sms import task as sms_task
from verifications import forms
import json

# 导入日志器
import logging

logger = logging.getLogger('django')


# Create your views here.

# 图片验证码
class ImageCode(View):
    def get(self, request, image_id):
        # 调用验证码生成库得到验证码图片和验证码
        text, image = captcha.generate_captcha()
        # 连接数据库
        con_redis = get_redis_connection('verify_codes')
        # 保存到数据库
        con_redis.setex('img_{}'.format(image_id), 300, text)
        # 日志器
        logger.info('log图片验证码：{}'.format(text))
        return HttpResponse(content=image, content_type='image/jpg')


# 用户名
class UsernameView(View):
    def get(self, request, username):
        """
        :param request:
        :param username:
        :return:json object
        """
        count = Users.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        # return JsonResponse({'data': data})
        return to_json_data(data=data)


# 手机号
class MobileView(View):
    def get(self, request, mobile):
        """
        :param request:
        :param mobile:
        :return:mobile/(?P<mobile>1[3-9]\d{9})/
        """
        data = {
            'count': Users.objects.filter(mobile=mobile).count(),
            'mobile': mobile
        }
        return to_json_data(data=data)


# 短信
class SmsCode(View):
    def post(self, request):
        """
        1，校验图片是否正确
        2，判断60秒内是否有发送记录
        3，构造6位短信验证码
        4，保存数据
        5，发送短信
        """
        json_str = request.body  # " mobile  text  iamge_code_id"
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数为空')
        dict_data = json.loads(json_str)
        form = forms.FromRegister(data=dict_data)

        if form.is_valid():
            mobile = form.cleaned_data.get('mobile')
            # 生成6位短信验证码
            sms_num = '%06d' % random.randint(0, 999999)

            # 构建外键
            con_redis = get_redis_connection('verify_codes')
            # 短信建  5分钟  sms_num
            sms_text_flag = "sms_{}".format(mobile).encode('utf8')
            # 过期时间
            sms_flag_fmt = 'sms_flag_{}'.format(mobile).encode('utf8')
            # 存
            con_redis.setex(sms_text_flag, 300, sms_num)
            con_redis.setex(sms_flag_fmt, 60, 1)  # 过期时间  1

            # 发送短信
            logger.info('短信验证码：{}'.format(sms_num))

            # 使用celery异步发送短信
            expires = 300
            sms_task.send_sms_code.delay(mobile, sms_num, expires, 1)
            return to_json_data(errmsg='短信验证码发送成功')

            # logging.info('发送短信验证码正常[mobile:%s,sms_num:%s]' % (mobile, sms_num))
            # return to_json_data(errmsg='短信验证码发送成功')

            # try:
            #     result = CCP().send_template_sms(mobile, [sms_num, 5], 1)
            # except Exception as e:
            #     logger.error('发送短信异常[mobile:%s message:%s]' % (mobile, e))
            #     return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
            # else:
            #     if result == 0:
            #         logging.info('发送短信验证码成功[mobile:%s,sms_num:%s]' % (mobile, sms_num))
            #         return to_json_data(errmsg='短信验证码发送成功')
            #     else:
            #         logging.info('发送短信验证码失败')
            #         return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
        else:
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)
