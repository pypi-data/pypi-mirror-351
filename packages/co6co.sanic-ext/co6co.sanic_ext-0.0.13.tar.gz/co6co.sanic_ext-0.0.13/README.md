# 扩展 sanic

# (sanic Demo)[https://www.osgeo.cn/sanic/sanic/examples.html/]

(task)[https://python.hotexamples.com/zh/examples/sanic/Sanic/add_task/python-sanic-add_task-method-examples.html]

# 历史记录

```
0.0.1 初始版本
0.0.2.
0.0.3 优化 baseView 2024-07-26
0.0.4
    baseView: save_file
0.0.5
    优化 result 模块
0.0.6
    增加 sanics.App 类 及 ViewManage
0.0.7
    BaseView : Content-Disposition，zip，head
    get_file_partial 方法
0.0.8 2025-01-08
    修复json中文bug
0.0.9 2025-03-05
    依赖  co6co.web-session
0.0.10 2025-03-24-3-28
    1. 新增　choose
    2.　优化： startApp 方法
    3. 增加主进程与子进程通信
0.0.11 2025-04-07
    1. response_head
0.0.12 2025-04-17
    1. 新增： getconfig for win package
0.0.13 2025-05-28
    1. bug
```

webSocket 测试地址
http://www.blue-zero.com/WebSocket/
http://coolaf.com/tool/chattest

这两个遇到个问题，sanic 一执行 websocket 地址 python 就报异常框（需 c++调试）的框
后经过一个个模块删除后发现是：
在文件夹中有 multidict-6.0.2 模块，`pip list` 显示确是 6.0.4，直接移除 multidict 发现正常

# 类属性与对象属性

```
class A:
    def __init__(self) -> None:
       self.a="12"
       pass

class B(A):
    b:str="abc"
    @classmethod
    def geA(cls) -> str:
        print(cls.a)
        return cls.a

a=A()
print(a.a)

b=B()
b.a="456"
print(b.a,B.a,"b.geA:", b.geA(),"B.geA:",B.geA())

a=A()
print(a.a,A.a)
```
