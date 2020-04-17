# import threading  # 多线程库
# from queue import Queue  # 队列
# import schedule
# import time
#
#
# def my_task():
#     # 任务
#     time.sleep(15)
#
#
# class MyQueue:
#     def __init__(self):
#         self.q = Queue()
#
#     def worker(self):
#         # 如果队列不为空则创建多线程任务
#         while not self.q.empty():
#             item = self.q.get()
#             task = threading.Thread(target=my_task, name=item)
#             task.start()
#
#
# def sche():
#     # 任务调度器,每隔20秒运行一次
#     schedule.every(20).seconds.do(my_queue.worker)
#     while True:
#         print('正在运行')
#         schedule.run_pending()
#         time.sleep(1)
#
#
# my_queue = MyQueue()
# # 要把任务调度器放在线程里
# task1 = threading.Thread(target=sche, name='schedule')
# # task1.start()


