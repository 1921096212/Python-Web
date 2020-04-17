from celery_tasks.main import app
from utils.yuntongxun.sms import CCP
import logging
logger = logging.getLogger('django')


@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_num, expires, temp_id):
    try:
        result = CCP().send_template_sms(mobile, [sms_num, expires], temp_id)
    except Exception as e:
        logger.error('发送短信异常[mobile:%s message:%s]' % (mobile, e))
        # return to_json_data(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
    else:
        if result == 0:
            logging.info('发送短信验证码成功[mobile:%s,sms_num:%s]' % (mobile, sms_num))
            # return to_json_data(errmsg='短信验证码发送成功')
        else:
            logging.info('发送短信验证码失败')
            # return to_json_data(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])

