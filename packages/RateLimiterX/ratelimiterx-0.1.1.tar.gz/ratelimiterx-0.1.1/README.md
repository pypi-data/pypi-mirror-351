# RateLimiterX
RateLimiterX提供在指定时间内执行指定数量的任务功能，并且可以指定执行速度。另外支持以下功能：  
1. 设置执行速率：尽可能平均执行、尽可能快地执行  
2. 支持多个任务队列，每个队列可单独设置任务、速率等，例如多个代理设置不同的速率  

## 使用说明
```
from ratelimiterx.ratelimiterx import RateLimiterX, Task, Speed
def example():
    rl = RateLimiterX(10 * 1000, 10)
    rate_limiterx_queue_id = init_ratelimiterx.create_queue(1000, 5)
    def fun1():
        # do something
        pass

    for i in range(10):
        init_ratelimiterx.add_task(rate_limiter_queue_id, Task(fun1))

    init_ratelimiterx.join()
    init_ratelimiterx.destroy()
```
                                                                       
## 项目说明
### 目录说明
- README.md: 包含使用手册、项目说明

### 执行依赖安装
pip install -r requirements.txt

### 依赖固化
pip freeze > requirements.txt

### 打包
1. pip install build
2. python -m build

### 发布到pypi
1. pip install twine  
2. python -m twine upload --repository pypi dist/*
3. 输入用户名和API Token。