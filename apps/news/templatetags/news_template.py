from django import template
'''
自定义分页页码过滤器
用于显示页面过多时用'...'代替
'''
register = template.Library()


@register.filter()
def page_bar(page):
    page_list = []
    # 头部
    if page.number != 1:
        page_list.append(1)
    if page.number - 3 > 1:
        page_list.append('...')
    if page.number - 2 > 1:
        page_list.append(page.number - 2)
    if page.number - 1 > 1:
        page_list.append(page.number - 1)
    page_list.append(page.number)
    # 尾部
    if page.paginator.num_pages > page.number + 1:
        page_list.append(page.number + 1)
    if page.paginator.num_pages > page.number + 2:
        page_list.append(page.number + 2)
    if page.paginator.num_pages > page.number + 3:
        page_list.append('...')
    if page.paginator.num_pages != page.number:
        page_list.append(page.paginator.num_pages)  # 返回总页数
    return page_list
