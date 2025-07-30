# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-09-30 09:57:16
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from ratelimiterx import RateLimiterX, Task
from utilsz import time_util

RATE_LIMIT_TIME_WINDOW = 20 * 1000
RATE_LIMIT_COUNT = 20


class SpiderTask:
    def __init__(self, url, fun, config, task_hash=None, extend=None):
        self.url = url
        self.fun = fun
        self.config = config
        self.hash = task_hash
        self.extend = extend
        self.future = None


class NetWorkError(Exception):
    def __init__(self, status_code=0, message='无'):
        super().__init__(f"网络请求错误，HTTP状态码: {status_code}, 错误信息: {message}")


class Scheduler(ThreadPoolExecutor):
    def __init__(self, max_workers=1, time_window=RATE_LIMIT_TIME_WINDOW, count=RATE_LIMIT_COUNT):
        super(Scheduler, self).__init__(max_workers)
        self.tasks = None
        self.rate_limiter = RateLimiterX(time_window, count)
        self.rate_limiter_queue_id = self.rate_limiter.create_queue()

    def submit_tasks(self, spider_task):
        if not spider_task:
            logging.error(f'spider_task is None')
            return
        self.tasks = spider_task
        for task in self.tasks:
            self.rate_limiter.add_task(self.rate_limiter_queue_id, Task(self.submit_fun, task))

    def submit_fun(self, task):
        """
        限流功能里回调的方法，限流对象里异步执行
        :param task: 待线程池里执行的用户任务
        :return:
        """
        task.future = super().submit(self.exec_fun, task)

    def exec_fun(self, task):
        """
        支持重试和延迟计制的任务执行
        :param task: 待线程池里执行的用户任务
        :return:
        """
        retries = 0
        exception = None
        while True:
            try:
                return task.fun(task.url, task.config)
            except NetWorkError as e:
                exception = e
                if (retries := retries+ 1) > task.config.RETRY_TIMES:
                    break
                logging.warning(f'{task.url} 获取失败：{exception}，准备重试第 {retries}/{task.config.RETRY_TIMES} 次')
                time_util.sleep_ms(task.config.RETRY_DELAY_MS)
        logging.error(f'{task.url} 获取失败：{exception}, 达到最大重试次数：{task.config.RETRY_TIMES}次')
        return None

    def result(self, task):
        while task.future is None:
            time_util.sleep_ms(50)
        return task.future.result()

    def cancel_tasks(self):
        for task in self.tasks:
            # 1.已结束的无法取消，取消返回失败
            # 2.进行中的不一定能取消，取消返回失败
            if task.future is None:
                continue
            task.future.cancel()

        while True:
            all_cancelled = True
            for task in self.tasks:
                if task.future is None:
                    continue
                if not task.future.done() and not task.future.cancelled():
                    all_cancelled = False
                    break
            if all_cancelled:
                break
            time.sleep(0.5)

    def get_progress(self):
        total_count = len(self.tasks)
        done_count = 0
        for task in self.tasks:
            if task.future.done():
                done_count += 1

        return done_count, total_count

    def destroy(self):
        self.rate_limiter.destroy()
