# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2025-05-07 17:17:12


import pytest

from src.ratelimiterx import RateLimiterX, Task, Speed
from utilsz import time_util


def _check_reslut(time_list, interval, deviation):
    """
    检测时间列表里每个时间是否小于某个值
    :param time_list: 需检测的时间列表
    :param interval: 检测每个执行的差值是否不大于interval
    :param deviation: 正偏差：因为执行时间因轮询间隔，只会比设定时间延后1-2个间隔，而不会提前执行
    :return:
    """
    # 检查结果
    if time_list is None or len(time_list) == 0:
        return False
    last_time = 0
    for time in time_list:
        if time == 0:
            return False
        if last_time == 0:
            last_time = time
            continue
        if (time - last_time) <= (interval + deviation):
            last_time = time
            continue
        else:
            return False
    return True


@pytest.fixture
def init_ratelimiterx():
    rl = RateLimiterX(10 * 1000, 10)
    return rl


def test_ratelimiterx_1(init_ratelimiterx: RateLimiterX):
    rate_limiter_queue_id = init_ratelimiterx.create_queue(1000, 5)
    fun_exec_time_list = []

    def fun1():
        fun_exec_time_list.append(time_util.get_cur_time_ms())

    for i in range(10):
        init_ratelimiterx.add_task(rate_limiter_queue_id, Task(fun1))

    init_ratelimiterx.join()
    init_ratelimiterx.destroy()
    # 200 至 200+2个轮询 之间
    print(f'time_list = {fun_exec_time_list}')
    assert _check_reslut(fun_exec_time_list, 200, init_ratelimiterx.loop_interval * 2)


def test_ratelimiterx_2(init_ratelimiterx: RateLimiterX):
    rate_limiter_queue_id = init_ratelimiterx.create_queue(1000, 5)
    fun_exec_time_list = []

    def fun1():
        fun_exec_time_list.append(time_util.get_cur_time_ms())
        time_util.sleep_ms(300)

    for i in range(10):
        init_ratelimiterx.add_task(rate_limiter_queue_id, Task(fun1))

    init_ratelimiterx.join()
    init_ratelimiterx.destroy()
    print(f'time_list = {fun_exec_time_list}')
    # 300 至 300+2个轮询 之间
    assert _check_reslut(fun_exec_time_list, 300, init_ratelimiterx.loop_interval * 2)


def test_ratelimiterx_3(init_ratelimiterx: RateLimiterX):
    rate_limiter_queue_id = init_ratelimiterx.create_queue(1000, 5, Speed.FAST)
    fun_exec_time_list = []

    def fun1():
        fun_exec_time_list.append(time_util.get_cur_time_ms())
        time_util.sleep_ms(50)

    for i in range(10):
        init_ratelimiterx.add_task(rate_limiter_queue_id, Task(fun1))

    init_ratelimiterx.join()
    init_ratelimiterx.destroy()
    print(f'time_list = {fun_exec_time_list}')

    assert _check_reslut(fun_exec_time_list, 50, init_ratelimiterx.loop_interval * 2)


def all_test():
    """
    手动执行所有用例，不用test开头是因为pytest会自动执行所有test开头的用例，从而导致所有用例执行2遍
    :return:
    """
    rl = init_ratelimiterx()
    test_ratelimiterx_1(rl)
    test_ratelimiterx_2(rl)
    test_ratelimiterx_3(rl)


if __name__ == '__main__':
    all_test()
