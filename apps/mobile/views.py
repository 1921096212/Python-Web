from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.

# 瀑布流页面
from utils.res_code import to_json_data
from mobile import models


def flow_image_view(request):
    return render(request, 'mobile/flow_image.html')


# 瀑布流json数据
def flow_image_json(request):
    # import pymongo
    # client = pymongo.MongoClient()
    # db = client['project1']['image']
    # a = db.find()
    # for i in a:
    #     print(i.get('name'))
    #     for x in i.get('url'):
    #         obj = models.FlowImage(title=i.get('name'), image_url=x)
    #         obj.save()
    page = int(request.GET.get('page', 1))
    images = models.FlowImage.objects.values('image_url')
    paginator = Paginator(images, 20)
    news_info = paginator.page(page)
    data = {
        'news': list(news_info),
        'total_pages': paginator.num_pages
    }
    return to_json_data(data=data)
