from __future__ import annotations
from sanic.blueprint_group import BlueprintGroup
from sanic import Sanic, utils, Blueprint
from sanic import Sanic, utils, Blueprint
from sanic_routing import Route
from typing import Optional, Callable, Any, Dict, List, overload
from pathlib import Path
from co6co.utils import log, File, try_except
from abc import ABC, abstractmethod


from sanic.worker.loader import AppLoader
from functools import partial
from co6co.utils.singleton import singleton
from co6co_sanic_ext.view_model import BaseView
from co6co_sanic_ext.api import add_routes
from datetime import datetime
from co6co.utils.source import compile_source
import inspect
from multiprocessing import Pipe
from multiprocessing.connection import PipeConnection
import asyncio
import threading
import multiprocessing
import os
import argparse


class Worker(ABC):
    """
    在主进程中增加一个工作进程，处理某些任务
    主进程与自进程进行通信
    child_conn.send()

    工作进程
    """

    def __init__(self, envent: asyncio.Event, parent_conn: PipeConnection):
        self.conn = parent_conn
        self.envent = envent

        self.isQuit = False
        self.thread = threading.Thread(target=self.worker, name="worker")  # , args=(conn,)

    # @property
    # def quit(self):
    #    """
    #    检查是否退出
    #    """
    #    return self.envent.is_set()

    @abstractmethod
    def handler(self, data: str, conn: PipeConnection):
        """
        处理数据
        抽象方法
        """
        print("收到数据：", data)
        # conn.send("ok")
        pass

    def stop(self):
        """
        退出
        """
        self.isQuit = True

    def start(self):
        self.thread.start()
        pass

    def worker(self):
        while True:
            try:
                if self.isQuit:
                    log.warn("worker thread quit by quit_event")
                    break
                data = self.conn.recv()   # 接收数据
                if self.handler:
                    self.handler(data, self.conn)

                    # log.warn("worker recv", data)
                    # self.conn.send("ok")  # 发送数据
                # self.scheduler.removeTask(data)
            except EOFError:
                log.warn("task worker quit by EOFError")
                break
            except IOError:
                log.warn("worker thread quit by IOError")
                break
            except Exception as e:
                log.warn("worker thread quit by Error", type(e), e)
                break
        log.warn("线程退出！")


def appendData(app: Sanic, **kwargs):
    """
    追加数据到app.ctx中
    """
    for key, value in kwargs.items():
        setattr(app.ctx, key, value)


def parserConfig(configFile: str):
    """
    一般 会有
    {  
      db_settings = {     }
      web_setting={}
    }
    """
    default: dict = {"web_setting": {'port': 8084, "backlog": 1024, 'host': '0.0.0.0', 'debug': False, 'access_log': True,  'dev': False}}
    customConfig = None
    if '.json' in configFile:
        customConfig = File.File.readJsonFile(configFile)
    else:
        customConfig = utils.load_module_from_file_location(Path(configFile)).configs
    if customConfig != None:
        default.update(customConfig)
    return default


def _create_App(name: str = "__mp_main__", configFile: str | Dict = None, apiInit: Callable[[Sanic, Dict, Sanic | None],  None] = None,  **kwargs):
    """
    创建应用
    将 config 中的配置信息加载到app.config中
    :param name: 应用名称
    :param config: 配置文件路径[json,py]
    :param apiMount: 挂载api

    return: app
    app.config.web_setting --> 配置信息
    """
    try:
        app = Sanic(name)
        data = locals()
        appendData(app, **kwargs)

        # primary = data.get("app", None)
        # app.ctx.mainApp = primary
        if configFile == None:
            raise PermissionError("config")
        if app.config != None:
            if type(configFile) == dict:
                customConfig = configFile
            else:
                customConfig = parserConfig(configFile)
            if customConfig != None:
                app.config.update(customConfig)
            # log.succ(f"app 配置信息：\n{app.config}")

            if apiInit != None:
                sig = inspect.signature(apiInit)
                params = sig.parameters
                all_param = [app, customConfig, data]
                # all_param = {"app":app,"customConfig": customConfig,"primary": primary}
                # arg_values = {}
                # for param_name, param in params.items():
                #    #如果参数没有默认值
                #    if param.default != inspect.Parameter.empty:
                #        arg_values[param_name] = param.default
                #    else:
                #        arg_values[param_name] = None
                par_len = len(params.items())
                apiInit(*all_param[:par_len])
        else:
            raise PermissionError("app config")
        return app
    except Exception as e:
        log.err(f"创建应用失败：\n{e}{repr(e)}\n 配置信息：{app.config}")
        raise


def startApp(configFile: str | Dict, apiInit: Callable[[Sanic, Dict], None], worker_loader: Callable[[Sanic, asyncio.Event, PipeConnection], Worker] = None):
    """
    __main__     --> primary
    __mp_main__  --> multiprocessing
    """

    # all_param = {**locals()}
    event = asyncio.Event()
    parent_conn, child_conn = Pipe()
    args = {"parent_conn": parent_conn, "child_conn": child_conn}
    loader = AppLoader(factory=partial(_create_App, configFile=configFile, apiInit=apiInit, **args))
    app = loader.load()
    setting: dict = app.config.web_setting
    app.prepare(**setting)
    appendData(app, quit_event=event)
    worker = None
    if worker_loader:
        worker = worker_loader(app, event, parent_conn)

    @try_except
    @app.main_process_start
    def start_app(app, loop):
        log.info("start_app...")
        if worker:
            worker.start()

    @try_except
    @app.main_process_stop
    def stop_app(app, loop):
        log.warn("stop_app.")
        event.set()  # 设置事件，通知其他协程
        child_conn.close()
        if worker:
            worker.stop()
        # 关闭数据库连接
    # 没有 primary serve 调用loader创建一个个
    Sanic.serve(primary=app, app_loader=loader)


def getConfigFilder(mainFilePath: str):
    dir = os.path.dirname(mainFilePath)
    return dir


def getConfig(configFolder: str):
    """
    当程序被打包后 if __name__ == "__main__" # 执行多次
    __file__ ==> _internal\\app.py
    __file__ ==> Temp\_MEI131322\\app.py
    """
    if os.name == "nt":  # 当程序被打包后 if __name__ == "__main__" # 执行多次
        multiprocessing.freeze_support()  # 进行打包时，需要添加这行代码,子进程将不在执行这下面的代码
    dir = configFolder
    defaultConfig = "{}/app_config.json".format(dir)
    configPath = os.path.abspath(defaultConfig)
    parser = argparse.ArgumentParser(description="System Service.")
    parser.add_argument("-c", "--config", default=configPath, help="default:{}".format(configPath))
    args = parser.parse_args()
    config = parserConfig(args.config)
    return config


@singleton
class ViewManage:
    """
    目标： 动态增加HTTPMethodView动态 api
    遇到的问题：取消以前增加的蓝图
    处理步骤：
        1. 应用初始化时从数据库中读出所有带增加的功能
        2. 将所有功能放在一个蓝图中， 统一一起增加
        3. 在平台中修改某个功能时需要，删除改功能并重新挂在到蓝图中
        4. 在平台中增加某想功能，需要在蓝图中增加
    """
    viewDict: Dict[str, BaseView] = None
    app: App = None
    bluePrint: Blueprint = None
    createTime: datetime = None

    @staticmethod
    def static_fun():
        """
        当静态方法遇上,单例模式中的
        """
        print("ddd")

    def __init__(self,  app: Sanic) -> None:
        super().__init__()
        self.viewDict = {}
        self.app = App(app)

    def _createBlue(self, blueName: str, url_prefix: str, version: int | str | float | None = 1, *views: BaseView):
        blue = Blueprint(blueName, url_prefix=url_prefix, version=version)
        add_routes(blue, *views)
        return blue

    def exist(self, blueName):
        return blueName in self.app.app.blueprints

    def add(self, blueName: str, url_prefix: str, version: int | str | float | None = 1, *views: BaseView):
        """
        BluePrint 名字不能与系统中存在的名字重复
        请求URL: /v{version}}/${url_prefix}/{BaseView.routePath}
        """
        blue = self._createBlue(blueName, url_prefix, version, *views)
        self.app.app.blueprint(blue)

    def _getUrls(self, url_prefix: str, version: int | str | float | None = 1, *views: BaseView):
        urls = ("/v{}{}{}".format(version, url_prefix, v.routePath) for v in views)
        return urls

    def replace(self, blueName: str, url_prefix: str, version: int | str | float | None = 1, *views: BaseView):
        if self.exist(blueName):
            blue = self._createBlue(blueName, url_prefix, version, *views)
            urls = self._getUrls(url_prefix, version, *views)
            self.app.remove_route(*urls)
            # 方法1 移除在按增加的来 服务器停止
            self.app.app.blueprints.pop(blueName)
            self.app.app.router.reset()
            self.app.app.blueprint(blue)
            # 方法2  简单替换无法实现功能，替换完还是以前的功能
            # self.app.app.blueprints[blueName]=blue
        else:
            raise Exception("Blueprint {} is Null".format(blueName))


class App:
    app: Sanic = None

    def __init__(self, app: Sanic = None) -> None:
        if app == None:
            app = Sanic.get_app()
        self.app = app
        pass

    def findRouteWithStart(self, url_prefix: str):
        routes = [r for r in self.app.router.routes if r.uri.startswith(url_prefix)]
        return routes

    def findOneRoute(self, uri: str):
        routes = [r for r in self.app.router.routes if r.uri == uri]
        if len(routes) == 1:
            return routes[0]
        return None

    def remove_route(self, *uri: str):
        """
        动态删除路由
        """
        routes = [r for r in self.app.router.routes if r.uri in uri]

        for r in routes:
            if r in self.app.router.routes:
                # self.app.router.reset()
                del self.app.router.routes[r]  # 元组无发删除

    # 动态替换路由
    def replace_route(self, uri, handler, methods=None):
        """
        替换路由
        """
        self.remove_route(uri)
        self.app.add_route(handler, uri, methods=methods)

    @staticmethod
    def appendView(app: Sanic, *viewSource: str,  blueName: str = "user_append_View", url_prefix="api", version=1, ingoreView: List[str] = ["AuthMethodView", 'BaseMethodView']):
        """
        增加视图
        前置条件: 1. 视图名不能重名
                 2. api地址不能重复
                 3.
        """
        try:
            viewMage = ViewManage(app)
            AllView: List[BaseView] = []
            nameList = []  # 路由名称不能重复
            routeUrl = []

            if len(viewSource) > 0:
                for s in viewSource:
                    globals_vars = {}
                    compile_source(s, globals_vars)
                    views: List[BaseView] = [globals_vars[i] for i in globals_vars if str(i).endswith("View") and i not in ingoreView]
                    for v in views:
                        if v.__name__ in nameList:
                            log.warn("视图名称‘{}’重复".format(v.__name__))
                            continue
                        if v.routePath in routeUrl:
                            log.warn("视图路由‘{}’重复".format(v.routePath))
                            continue
                        nameList.append(v.__name__)
                        routeUrl.append(v.routePath)
                        AllView.append(v)
            if len(AllView) > 0:
                viewMage.add(blueName, url_prefix, version, *AllView)
        except Exception as e:
            log.err("动态模块失败", e)
