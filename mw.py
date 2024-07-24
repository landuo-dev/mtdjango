import time

def my(func):
    def inner(request):
        print("这是我的装饰器")
        start = time.time()
        res = func(request)
        end = time.time()
        print("执行时间：", end - start)
        return res
    return inner


