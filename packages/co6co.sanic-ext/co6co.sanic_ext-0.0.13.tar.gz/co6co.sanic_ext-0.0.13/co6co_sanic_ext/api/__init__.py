
from sanic import Sanic, Blueprint, Request
from ..view_model import BaseView


def add_routes(blue: Blueprint, *views: BaseView):
    """
    增加路由
    """
    for v in views:
        blue.add_route(v.as_view(), v.routePath, name=v.__name__)
