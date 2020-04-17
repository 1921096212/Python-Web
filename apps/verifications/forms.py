from django.core.validators import RegexValidator
from django import forms

# 创建手机号的正则校验器
from django_redis import get_redis_connection

mobile_validator = RegexValidator(r"^1[3-9]\d{9}$", "手机号码格式不正确")


class FromRegister(forms.Form):
    """
        check image code
        """
    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validator, ],
                             error_messages={"min_length": "手机号长度有误", "max_length": "手机号长度有误",
                                             "required": "手机号不能为空"})
    image_code_id = forms.UUIDField(error_messages={"required": "图片UUID不能为空"})
    text = forms.CharField(max_length=4, min_length=4,
                           error_messages={"min_length": "图片验证码长度有误", "max_length": "图片验证码长度有误",
                                           "required": "图片验证码不能为空"})

    def clean(self):
        # 继承父类clean 方法   复用校验
        cleaned_data = super().clean()
        mobile_num = cleaned_data.get('mobile')
        image_uuid = cleaned_data.get('image_code_id')
        image_text = cleaned_data.get('text')

        # 1、获取图片验证码
        con_redis = get_redis_connection(alias='verify_codes')
        img_key = "img_{}".format(image_uuid).encode('utf-8')
        redis_img_code = con_redis.get(img_key)  # b'ABCD'  # False
        # 取完就删掉
        con_redis.delete(img_key)
        # if not real_image_code_origin:
        #     real_image_code = None
        # else:
        #     real_image_code = real_image_code_origin.decode('utf8')    # 'ABCD'
        # 判断uuid为空返回none否则赋值redis_img_code返回
        real_image_code = redis_img_code.decode('utf8') if redis_img_code else None

        # 2、判断用户输入的图片验证码与数据库取得是否一致
        if image_text.upper() != real_image_code:
            raise forms.ValidationError("图片验证码校验失败")

        # 3、判断在60秒内是否有发送短信的记录
        if con_redis.get("sms_flag_{}".format(mobile_num)):
            raise forms.ValidationError("获取短信验证码过于频繁")
        return cleaned_data
