import datetime
from typing import Any, Dict
from sanic.response import json as res_json
import json as sys_json


class JSON_util(sys_json.JSONEncoder):
    @classmethod
    def json(cls, data: Any, status: int = 200, headers: Dict[str, str] | None = None):
        jsonEncoder = object.__new__(cls)
        return res_json(jsonEncoder.encode(data), status, headers)

    def default(self, obj: Any) -> Any:
        # print("JSON_Util:",obj,"-->",type(obj))
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        elif isinstance(obj, int):
            return int(obj)
        elif isinstance(obj, float):
            return float(obj)
        elif isinstance(obj, tuple):
            return str(obj)
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        return None

    def response(res: any, jsonEncoder: sys_json.JSONEncoder = None, **kwargs):
        if jsonEncoder == None:
            # JSON_util(ensure_ascii=False)
            return res_json(sys_json.loads(JSON_util().encode(res)), **kwargs)
        else:
            return res_json(sys_json.loads(jsonEncoder.encode(res)), **kwargs)
