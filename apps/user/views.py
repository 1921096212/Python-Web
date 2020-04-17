import json

from django.shortcuts import render, redirect, reverse  # render渲染页面redirect页面跳转reverse反向解析路由
from django.views import View

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from my_news.settings import MOBILE_FILE
import os

from .models import Users
from utils.res_code import to_json_data, Code, error_map
from .froms import RegisterForm, LoginForm
from django.contrib.auth import login, logout

from django.http import JsonResponse

import logging

logger = logging.getLogger('django')


# 用户登录
class Login(View):
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        """
        1.得到由ajax传来的数据
        2.把传来的json转化dict
        3.传到表单里校验合法性
        4.在表单里查询与数据库的账户信息是否一致
        :param request:
        :return:
        """
        json_data = request.body  # 从前台ajax传过来json类型的数据
        if not json_data:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))  # 把传过来的json转化为dict
        form = LoginForm(data=dict_data, request=request)  # 表单验证
        if form.is_valid():  # 判断表单有没有错误
            return to_json_data(errmsg="恭喜您，登录成功！")
        else:
            # 返回错误列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 用户登出
class Logout(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('user:login'))


# 用户注册
class Register(View):
    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        """
        1用户名2密码3确认密码4mobile5短信验证码
        :param request:
        :return:
        """
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg=[error_map[Code.PARAMERR]])
        # 把json转化为python字典
        data_dict = json.loads(json_str.decode('utf8'))
        # 传到表单
        form = RegisterForm(data=data_dict)

        if form.is_valid():  # is_valid:如果表单没有错误，则返回True，否则返回False。
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')
            user = Users.objects.create_user(username=username, password=password, mobile=mobile)
            # 第一个参数 request obj 第二个 user obj
            login(request, user)
            return to_json_data(errmsg='注册成功')
        else:
            # 返回错误列表
            err_msg_list = []
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
            err_msg_str = '/'.join(err_msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 小练习
# class Test(View):
#     """
#     队列与多线程的可视化
#     """
# from .test import threading, my_queue
#
#     def get(self, request):
#         name = threading.enumerate()  # 线程名字
#         count = threading.active_count()  # 线程数量
#         waiting_queue = my_queue.q.qsize()  # 队列数量
#         context = {
#             'name': name,
#             'count': count,
#             'waiting_queue': waiting_queue,
#         }
#         return render(request, 'test/form.html', context=context)
#
#     def post(self, request):
#         json_data = request.body
#         if not json_data:
#             return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
#         dict_data = json.loads(json_data.decode('utf8'))
#         name = dict_data.get('user_account')
#         # 添加队列
#         my_queue.q.put(name)
#
#         return to_json_data(errmsg=threading.current_thread().name)  # 当前线程名称


def params_first(request):
    """
    如果有人访问网站主页,获取访问者公网ip,存到日志里
    :param request:
    :return:
    """
    ip = request.GET.get('pwd', '')  # 直接从GET请求中获取参数
    logger.info('游客ip:{}'.format(ip))
    return HttpResponse()


def catchphrase(request):
    """
    名言警句接口
    :param request:
    :return:
    """
    import random

    data = [
        '最好的，缺乏说服力，而最糟糕的，是充满激情的强度。——W.B.叶芝',
        '我们这个时代让人困扰的事之一是：那些对事确信无疑的人其实很蠢，而那些富有想象力和理解力的人却总是怀疑和优柔寡断。——贝特朗·罗素',
        '无知要比博学更容易产生自信。—— 查尔斯·达尔文',
        '我的人生正是：使事业成为喜悦，使喜悦成为事业。—— 罗素',
        '很多事、经历了、才明白、风一场。谁也不是谁的谁、谁也成不了谁的谁。唯一成为永恒的真理是、照顾好自己、别渴望别人。',
        '勇敢的做自己，不要为任何人而改变。如果他们不能接受最差的你，也不配拥有最好的你。至于未来会怎样，要用力走下去才知道，先变成更喜欢的自己，路还长，天总会亮。',
        '在现代生活的条件下，规律是绝对的，凡是不重视有训练的智慧的民族是注定要失败的。—— 罗素',
        '做老师的只要有一次向学生撒谎撒漏了底，就可能使他的全部教育成果从此为之毁灭。—— 卢梭',
        '别让生活的压力挤走快乐，不管昨天发生了什么，不管昨天的自己有多难堪，有多无奈，有多苦涩，都过去了，不会再来，也无法更改。就让昨天把所有的苦、所有的累、所有的痛远远地带走吧，而今天，要收拾心情，继续前行。让豁达成为习惯，坦然面对生活中的喜怒哀乐，用心去感受生活，生活就会给你回报。',
        '古今之成大事业、大学问者，必经过三种之境界：“昨夜西风凋碧树，独上高楼，望尽天涯路”，此第一境界也；“衣带渐宽终不悔，为伊消得人憔悴”，此第二境界也；“众里寻他千百度，蓦然回首，那人却在灯火阑珊处”，此第三境界也。',
        '出外经商的人，拾着银钱盘缠，远走江湖运货贩卖到四方，白天要防备风雨折损，夜里要提防暴徒抢劫，陆上贩运要防备贪官污吏刁难，到了市场之上又要防备经纪人盘剥。有时不免忍饥挨饿，风餐露宿，其艰辛真是难以言状。',
        '原谅我经常明明狠在乎，却装出无所谓的态度。',
        '大器不必晚成，趁着年轻，努力让自己的才能创造最大的价值。最快乐的人并不是一切东西都是最好的，但他们会充分享受自己已有的东西。',
        '世界太大，生命太短，要过得尽量像自己想要的样子才对。做一个素净的人，把目光停留在微小而光明的事物上，远离那些混乱和嚣张。',
        '人们常常被一句“以后怎么办”给吓退了。以后那么长，不是想出来的，是过出来的。',
        '向他的头脑中灌输真理，只是为了保证他不在心中装填谬误。—— 卢梭',
        '精诚所至，金石为开。伟大的作品，不是靠力量而是靠坚持才完成的。成功是一段路程，而非终点，所以只要在迈向成功的过程中一切顺利，便是成功。毅力是永久的享受。',
        '我曾相信，所有值得知道之事，我在剑桥都知道了。在我旅行的过程之中，这一想法逐渐消失了。这与我本意相反，但是却对我非常有益。—— 罗素',
        '生活平平淡淡，早起与家人互道早安；父母健康长寿，尽量天天见面；孩子聪明可爱，每天亲亲小脸；夫妻恩爱有加，一生把手相牵；生活无需复杂，幸福就是如此简单。',
        '只要有学问，无论地位高低，年纪大小，人人都可以作为自己的老师。',
        '如果在胜利前却步，往往只会拥抱失败；如果在困难时坚持，常常会获得新的成功。死脑筋的人相信命运，活脑筋的人相信机会。',
        '点点滴滴的藏，集成了一大仓。泰山不让土壤，故能成其大；河海不择细流，故能就其深。为学须刚与恒，不刚则隋隳，不恒则退。为学犹掘井，井愈深土愈难出，若不快心到底，岂得见泉源乎？',
        '特喜欢人家吧？特放不下人家吧？觉得自己特委屈吧？呵呵，结果呢？人家烦了吧？人家嫌你矫情了吧？人家觉得你多余了吧？人家不待见你了吧？人家不理你了吧？你没话找话人家回复不过仨字了吧？当你特别在乎一个人的时候，那个人就不会在乎你了，你怎么就永远不懂？',
        '不想认命，就去拼命！付出就会有收获，或大或小，或迟或早，始终不会辜负你的努力！有一种落差是，你总是羡慕别人的成功，自己却不敢开始！你配不上自己的野心，也辜负了所受的苦难。',
        '我们要提出两条教育的诫律。一条“不要教过多的学科”另一条，“凡是你所教的东西，要教得透彻”。—— 罗素',
        '困厄无疑是个很好的老师；然而这个老师索取的学费很高，学生从他那里所得到的时常还抵不上所缴的学费。—— 卢梭',
        '不经一番彻骨寒，哪有梅花扑鼻香？表示惊讶，只需一分钟；要做出惊人的事业，却要许多年。耐心之树，结黄金之果。斧头虽小，但经历多次劈砍，终能将一棵最坚硬的橡树砍倒。',
        '岁月就如年轮般给你罩上一层又一层。如有一天，你想看看当初纯粹的样子，就要拨开早已融入肌肤的年轮，这是一种刻骨铭心的记忆。经典说说大全，抓一把梦的土壤，将心底记忆的种子成长为一棵参天大树。人活一世，躯体迟早要归还于尘土，现在看来，能在旅途中留下记录，是一件多么好的事情。',
        '你改变不了环境，但你可以改变自己；你改变不了事实，但你可以改变态度；你改变不了过去，但你可以改变现在；你不能控制他人，但你可以掌握自己；你不能预知明天，但你可以把握今天；你不可以样样顺利，但你可以事事尽心；你不能延伸生命的长度，但你可以决定生命的宽度。',
        '果断的放弃是面对人生面对生活的一种清醒的选择。活着，谁都有疲惫，有迷茫。人都有自己的做人之志和生存之道，最终归结为道德底线。',
        '我们栽培草木，使它长成一定的样子，我们教育人，使他具有一定的才能。—— 卢梭',
        '爱情是需要某程度的付出，爱是有代价的，爱是甜蜜的，爱是两个人之间要互相尊重、关怀，最新经典说说短语，爱可以令一个人突然变得很大胆、很勇敢，而且不会退缩，会坚持到底。当有一天你发现自己不再坚持的时候，就已经没有爱了。',
        '我行过许多地方的桥，看过许多次数的云，喝过许多种类的酒，却只爱过一个正当最好年龄的人。每天醒来告诉自己，只要信念还在，一切都还来得及。',
        '战争不决定谁对了，只决定谁留下了。',
        '乞丐并不会妒忌百万富翁，但是他肯定会妒忌收入更高的乞丐。',
        '你能在浪费时间中获得乐趣，就不是浪费时间。',
        '一切伟大的著作都有令人生厌的章节，一切伟人的生活都有无聊乏味的时候。',
        '人的一生就应该像一条河，开始是涓涓细流，被狭窄的河岸所束缚，然后，它激烈地奔过巨石，冲越瀑布。渐渐地，河流变宽了，两边的堤岸也远去，河水流动得更加平静。最后，它自然地融入了大海，并毫无痛苦地消失了自我。',
        '爱情只有当它是自由自在时，才会叶茂花繁。认为爱情是某种义务的思想只能置爱情于死地。只消一句话：你应当爱某个人，就足以使你对这个人恨之入骨。',
        '如果一听到一种与你相左的意见就发怒，这表明，你已经下意识地感觉到你那种看法没有充分理由。如果某个人硬要说二加二等于五，你只会感到怜悯而不是愤怒。',
        '我绝不会为我的信仰而献身，因为我可能是错的。',
        '这个世界的问题在于聪明人充满疑惑，而傻子们坚信不疑。',
        '言论自由只有在政府认为它自身安全的时候才存在。',
        '不用盲目地崇拜任何权威，因为你总能找到相反的权威。',
        '幸福的秘诀是：尽量扩大你的兴趣范围，对感兴趣的人和物尽可能友善。',
        '人的情绪起落是与他对事实的感知成反比的，你对事实了解得越少，就越容易动感情。',
        '人生而无知，但是并不愚蠢，是有些教育使人愚蠢。',
        '只凭阅读本身并不能提高我们对任何事物的理解能力。如果一生中能读到一本好书，在阅读中又感到乐趣，这种乐趣又把我们引深到思考中去，在思辨中再得到更大的乐趣，这才是一本好书应有的价值，也是它真正存在的意义。',
        '眼光长远是理性的，但也是苦闷的，因为美好永远在将来，当下永远有苦难。',
        '放弃自己想要的某些东西是幸福生活不可或缺的一部分。',
        '使我们无法自由和高尚地活着的最主要原因是对财富的迷恋。',
        '欲望使人即使到了天堂也会坐立不安。',
        '希望是坚韧的拐杖，忍耐是旅行袋，携带它们，人可以登上永恒之旅。',
        '人之所以有道德 是因为受到的诱惑还不够大。',
        '一个有勃勃生机与广泛兴趣的人，可以战胜一切不幸。一个明智地追求快乐的人，除了培养生活赖以支撑的主要兴趣之外，总得设法培养其他许多闲情逸致 。',
        '所谓幸福的生活，必然是指安静的生活，原因是只有在安静的气氛中，才能够产生真正的人生乐趣。',
        '传统的人看到背离传统的行为就大发雷霆，主要是因为他们把这种背离当作对他们的批评。',
        '人的真实生活不在于穿衣吃饭，而在艺术、思想和爱，在于美的创造和瞑想以及对于世界的合乎科学的了解。',
        '在一切道德品质之中，善良的本性在世界上是最需要的。',
        '一切社会的不平等，从长远看来，都是收入上的不平等。',
        '第一条是：记住你的动机并不总像你想象的那么有益于他人。第二条是：不要过高估计你自己的价值。第三条是：不要期望他人能像你那样注意你。第四条是：不要以为多数人都在设法迫害你。',
        '忍受单调生活的能力，应当从小培养。现代父母在这方面真该大受谴责；他们供给子女的消极娱乐实在太多，如电影、美食之类，他们不懂得平淡的生活对于儿童的重要性。',
        '只有同这个世界结合起来，我们的理想才能结出果实；脱离这个世界，理想就不结果实。',
    ]
    return to_json_data(data=data[random.randint(0, len(data)) - 1])


# 上传文件功能
@csrf_exempt
def upload(request):
    if request.method == "GET":
        return render(request, 'test/upload_test.html')
    if request.method == "POST":
        file = request.FILES.get('file')
        file_name = os.path.join(MOBILE_FILE, file.name)
        if os.path.exists(file_name):
            # print('文件已存在:%s' % file_name)
            return HttpResponse('文件已存在')
        with open(file_name, 'wb') as f:
            for i in file.chunks():
                f.write(i)
        return HttpResponse('ok')


# ----------------------------移动端接口----------------------------
@csrf_exempt
def api_view(request):
    """
    与手机app通讯
    字段 参数 简介 返回值
    1   stop  关闭监测器 自身
    2   无   获取当前手机状态(ip,网络状态)   ip
    3   列表[文件夹路径]   获取文件夹下所有文件名 列表[文件名]
    4   列表[文件路径]    获取文件    路径
    5   列表[文件路径]    获取文件夹的大小    列表[文件大小]
    times   秒   监测器刷新时间
    :param request:
    :return:
    """
    if request.method == 'GET':
        # 控制器
        data = {
            'name': 3,
            # 'arg': 'DCIM/图虫'
            'arg': '/',
            'times': 1000 * 7,
        }
        return JsonResponse(data)

    if request.method == 'POST':
        data = request.body
        dict_data = json.loads(data.decode('utf8'))
        file_path = os.path.join(MOBILE_FILE, dict_data.get("Keys").split('/')[-1])
        if os.path.exists(file_path):
            print('文件已经上传过了', file_path)
            return HttpResponse(dict_data.get("Keys"))
        print(dict_data)
        return HttpResponse('ok')


# 手机app启动时的启动页面
def index(request):
    return render(request, 'mobile/index.html')
