from django import forms
from django.contrib.auth import login
from django_redis import get_redis_connection
import re
from django.db.models import Q

from user import constants
from .models import Users


class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=20, min_length=5,
                               error_messages={"min_length": "用户名长度要大于5",
                                               "max_length": "用户名长度要小于20",
                                               "required": "用户名不能为空"}
                               )
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6",
                                               "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"}
                               )
    password_repeat = forms.CharField(label='确认密码', max_length=20, min_length=6,
                                      error_messages={"min_length": "密码长度要大于6",
                                                      "max_length": "密码长度要小于20",
                                                      "required": "密码不能为空"}
                                      )
    mobile = forms.CharField(label='手机号', max_length=11, min_length=11,
                             error_messages={"min_length": "手机号长度有误",
                                             "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})

    sms_code = forms.CharField(label='短信验证码', max_length=6, min_length=6,
                               error_messages={"min_length": "短信验证码长度有误",
                                               "max_length": "短信验证码长度有误",
                                               "required": "短信验证码不能为空"})

    # 判断用户名或或手机号是否注册
    def clean_mo_un(self):
        users = self.cleaned_data.get('username')
        tel = self.cleaned_data.get('mobile')
        if Users.objects.filter(username=users, mobile=tel).exists():  # 查询数据是否存在
            raise forms.ValidationError("用户名或手机号已注册，请重新输入！")
        return users, tel

    def clean(self):
        cleaned_data = super().clean()
        passwd = cleaned_data.get('password')
        passwd_repeat = cleaned_data.get('password_repeat')

        if passwd != passwd_repeat:
            raise forms.ValidationError("两次密码不一致")

        tel = cleaned_data.get('mobile')
        sms_text = cleaned_data.get('sms_code')

        # 建立redis连接
        redis_conn = get_redis_connection(alias='verify_codes')
        sms_fmt = "sms_{}".format(tel).encode('utf8')
        real_sms = redis_conn.get(sms_fmt)  # 在数据库里去获取
        if (not real_sms) or (sms_text != real_sms.decode('utf-8')):
            raise forms.ValidationError("短信验证码错误")


class LoginForm(forms.Form):
    user_account = forms.CharField()
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={"min_length": "密码长度要大于6",
                                               "max_length": "密码长度要小于20",
                                               "required": "密码不能为空"})
    remember_me = forms.BooleanField(required=False)

    # 复用表单
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)

    # 拿到用户名判断合法性
    def clean_user_account(self):
        user_info = self.cleaned_data.get('user_account')
        if not user_info:
            raise forms.ValidationError('用户账号不能为空')
        if not re.match(r'^1[3-9]\d{9}$', user_info) and (len(user_info) < 5 or len(user_info) > 20):
            raise forms.ValidationError('用户账号格式不正确,请重新输入')
        return user_info

    def clean(self):
        cleaned_data = super().clean()
        # 获取清洗后的数据
        user_info = cleaned_data.get('user_account')
        passwd = cleaned_data.get('password')
        hold_login = cleaned_data.get('remember_me')
        # 到数据库里查询用户名是否存在
        user_queryset = Users.objects.filter(Q(mobile=user_info) | Q(username=user_info))  # 满足任意条件
        if user_queryset:
            user = user_queryset.first()  # 返回查询的第一个对象，如果没有找到匹配，则返回None。
            if user.check_password(passwd):  # 判断密码是否正确
                if hold_login:  # 如果勾选记住密码
                    self.request.session.set_expiry(constants.USER_SESSION_EXPIRES)  # 保存时间
                else:
                    self.request.session.set_expiry(0)  # 浏览器关闭就清除session
                login(self.request, user)  # 本地保存用户登录信息
            else:
                raise forms.ValidationError('密码错误,请重新输入')
        else:
            raise forms.ValidationError('用户账号不存在,请重新输入')
