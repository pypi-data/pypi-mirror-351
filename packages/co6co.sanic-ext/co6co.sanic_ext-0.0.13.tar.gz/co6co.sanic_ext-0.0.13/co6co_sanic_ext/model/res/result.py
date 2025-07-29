# -*- encoding:utf-8 -*-
# Result 在 db_ext 中已经存在，是否应删除，需要验证正式使用的是那个模块
from __future__ import annotations


class dictType:
    def checkHasAttr(self, attrFiled, filedValue: None):
        if not hasattr(self, attrFiled):
            self[attrFiled] = filedValue

    def __init__(self) -> None:
        self._dict = {}
        pass

    def __setitem__(self, key, value):
        """ 设置属性 """
        self._dict[key] = value

    def __getitem__(self, key):
        """ 获取属性 """
        return self._dict.get(key, None)


class Result:
    code: int
    message: str
    data: any
    '''
    def __new__(cls, **kvargs) -> Result:
        print("__new__", cls)
        instance: Result = super(Result, cls).__new__(cls)
        instance.__dict__.update(kvargs)
        return instance
    '''

    def __init__(self,  code: int = 0, message=None, data: any = None, **kvargs) -> None:
        self.code = code
        self.message = message
        self.data = data
        self.__dict__.update(kvargs)
        pass

    @staticmethod
    def success(data: any = None, message: str = "操作成功", **kvargs) -> Result:
        return Result(data=data, code=0, message=message, **kvargs)

    @staticmethod
    def fail(data: any = None, message: str = "处理失败", **kvargs) -> Result:
        return Result(data=data, code=500, message=message, **kvargs)

    def __repr__(self) -> str:
        return f"class=> <code:{self.code},message:{self.message},data:{self.data}>"


class Page_Result(Result):
    total: int = -1
    '''
    def __new__(cls, **kvargs) -> Page_Result:
        # self = object.__new__(cls)
        instance: Page_Result = super(Page_Result, cls).__new__(cls, **kvargs)
        instance.checkHasAttr("total", -1)
        return instance
    '''

    def __init__(self, code: int = 0, message=None, data: any = None, total: int = -1, **kvargs) -> None:
        super().__init__(code, message, data, **kvargs)
        self.total = total

    @staticmethod
    def success(data: any = None, message: str = "操作成功", total: int = -1, **kvargs) -> Page_Result:
        return Page_Result(data=data, code=0, message=message, total=total, **kvargs)

    @staticmethod
    def fail(data: any = None, message: str = "处理失败", total: int = -1, **kvargs) -> Page_Result:
        return Page_Result(data=data, code=500, message=message, total=total, **kvargs)

    def __repr__(self) -> str:
        return f"class=> <code:{self.code},message:{self.message},total:{self.total},data:{self.data}>"
