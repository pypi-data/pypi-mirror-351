# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2025-05-06 15:29:25
import logging
from enum import Enum
from threading import Thread

from utilsz import time_util


class Speed(Enum):
    AVERAGE = 0
    """队列中任务在时间窗口内尽可能匀速执行"""
    FAST = 1
    """队列中任务在时间窗口内尽可能快地执行"""


class Task:
    id_suffix = 0

    def __init__(self, fun, *args, **kwargs):
        """
        队列里执行的任务
        :param fun: 执行的函数
        :param args: 执行的函数传递的参数
        :param kwargs: 执行的函数传递的参数
        """
        self.fun = fun
        self.args = args
        self.kwargs = kwargs
        self.id = f'Task{Task.id_suffix}'
        '''任务唯一标记，例如Task0'''
        Task.id_suffix += 1
        self.exec_time = 0
        '''执行时的时间'''

    def __repr__(self):
        return f'{self.id} {time_util.ms_to_datetime(self.exec_time, '%H:%M:%S.%f')}'


class Queue:
    """
    任务队列，每个队列可设置不同的限速参数，例如时间窗口、任务数量、速度等
    """
    id_suffix = 0

    def __init__(self, time_ms: int = 0, count: int = 0, speed: Speed = Speed.AVERAGE, extra=None):
        self.id = f'Queue{Task.id_suffix}'
        Task.id_suffix += 1
        self.count = count
        self.time_ms = time_ms
        self.speed = speed
        self.task_list = []
        self.extra = extra
        self.destroy_flag = False
        self.task_all_done = True

    def __repr__(self):
        return f'{self.id} {self.count}次 {self.time_ms}ms {self.speed} {self.extra}'


class RateLimiterX:
    """
    RateLimiterX提供在指定时间内执行指定数量的任务功能，并且可以指定执行速度。另外支持以下功能：
    1. 设置执行速率：尽可能平均执行、尽可能快地执行
    2. 支持多个任务队列，每个队列可单独设置任务、速率等，例如多个代理设置不同的速率
    """

    def __init__(self, time_window: int, count: int, speed: Speed = Speed.AVERAGE, loop_interval=50):
        """
        :param time_window: 时间窗口
        :param count: 时间窗口内执行任务的最多数量
        :param speed: Mode.AVERAGE：在时间窗口内平均执行任务；Mode.FAST：在时间窗口内尽快执行任务；
        """
        self.count = count
        self.time_ms = time_window
        self.speed = speed
        self.loop_interval = loop_interval
        '''任务循环遍历时的时间间隔'''

        self.queue_list = []
        self.run_flag = True
        """是否遍历队列和任务"""
        self.thread = Thread(target=self.run)
        self.thread.start()

    def create_queue(self, time_window: int = None, count: int = None, speed: Speed = None) -> str:
        """
        创建并添加队列
        :param time_window: 该队列的限速的时间窗口
        :param count: 该队列时间窗口内执行任务的最多数量
        :param speed: 该队列时间窗口内执行速度
        :return: 任务的id
        """
        if time_window is None:
            time_window = self.time_ms
        if count is None:
            count = self.count
        if speed is None:
            speed = self.speed
        queue = Queue(time_window, count, speed)
        self.queue_list.append(queue)
        return queue.id

    def find_queue_by_id(self, queue_id: str) -> Queue or None:
        """
        通过队列id查找队列
        :param queue_id: 队列id
        :return: 找到的队列或None
        """
        queue_target = None
        if queue_id is None:
            return None
        for queue in self.queue_list:
            if queue.id == queue_id:
                queue_target = queue
                break
        return queue_target

    def debug_queue(self, queue: Queue):
        """
        通过logging输出队列信息和任务信息
        :param queue:
        :return:
        """
        debug_str = f'{queue}: '
        for task in queue.task_list:
            debug_str += f'[{task}], '
        logging.debug(debug_str)

    def _run_queue(self, queue: Queue):
        """
        队列遍历任务并执行
        :param queue: 队列
        """
        window_end = time_util.get_cur_time_ms()
        window_start = window_end - queue.time_ms
        task_begin_in_window = -1
        task_count_in_window = 0
        task_target = None
        task_target_index = -1
        for index, task in enumerate(queue.task_list):
            if task.exec_time == 0 and task_target is None:
                task_target = task
                task_target_index = index
            if window_start <= task.exec_time <= window_end:
                if task_begin_in_window == -1:
                    task_begin_in_window = index
                task_count_in_window += 1
        # 没有可执行任务
        if task_target is None:
            queue.task_all_done = True
            return
        queue.task_all_done = False
        # 清除时间窗口之前的任务
        if task_begin_in_window > 1:
            queue.task_list[:task_begin_in_window - 1] = []

        if queue.speed == Speed.AVERAGE:
            # 1. 窗口内执行次数小于指定数量
            # 2. 每次请求保持一定间隔
            if task_count_in_window < queue.count:
                average_interval = queue.time_ms / queue.count
                if task_count_in_window == 0 or (
                        window_end > (queue.task_list[task_target_index - 1].exec_time + average_interval)):
                    task_target.exec_time = time_util.get_cur_time_ms()
                    task_target.fun(*task_target.args, **task_target.kwargs)
                    self.debug_queue(queue)
        elif queue.speed == Speed.FAST:
            # 1. 窗口内执行次数小于指定数量
            if task_count_in_window < self.count:
                task_target.exec_time = time_util.get_cur_time_ms()
                task_target.fun(*task_target.args, **task_target.kwargs)
                self.debug_queue(queue)
        return 1

    def add_task(self, queue_id: str, task: Task) -> bool:
        """
        添加任务到指定队列
        :param queue_id: 需添加到的任务的id
        :param task: 被添加的任务
        :return: 添加成功或失败
        """
        queue_target = self.find_queue_by_id(queue_id)
        if queue_target is None:
            return False
        queue_target.task_list.append(task)
        queue_target.task_all_done = False

    def run(self):
        """
        循环遍历队列和任务，并执行任务，直至对象被销毁
        :return:
        """
        while self.run_flag:
            for queue in self.queue_list:
                self._run_queue(queue)
            for i in range(len(self.queue_list) - 1, -1, -1):
                if self.queue_list[i].destroy_flag:
                    del self.queue_list[i]
            time_util.sleep_ms(self.loop_interval)

    def join(self, queue_id: str = None, timeout_ms: int = 0):
        """
        等待队列所有任务执行结束，否则一直等待
        :param queue_id: 等待的队列，如果为None则等待所有队列
        :param timeout_ms: 等待超时时间，超时后还未执行结束则立即返回，0则一直等待
        """
        queue = self.find_queue_by_id(queue_id)
        join_queue = []
        if queue is not None:
            join_queue.append(queue)
        else:
            join_queue = self.queue_list
        start_time = time_util.get_cur_time_ms()
        logging.debug(f'join queue list={join_queue}, timeout_ms={timeout_ms}')
        while True:
            if timeout_ms != 0 and (time_util.get_cur_time_ms() >= start_time + timeout_ms):
                break
            all_done = True
            for queue in join_queue:
                if not queue.task_all_done:
                    all_done = False
            if all_done:
                break
            time_util.sleep_ms(self.loop_interval)

    def destroy_queue(self, queue_id: str):
        """
        异步销毁指定队列
        :param queue_id:队列id
        """
        queue_target = self.find_queue_by_id(queue_id)
        queue_target.destroy_flag = True

    def destroy(self):
        """
        停止循环遍历
        """
        self.run_flag = False
