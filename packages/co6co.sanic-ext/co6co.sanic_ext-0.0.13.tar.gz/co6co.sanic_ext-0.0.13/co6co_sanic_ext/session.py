from co6co_web_session import Session, IBaseSession, MemorySessionImp
from sanic.app import Sanic


def init(app: Sanic, sessionImp: IBaseSession = MemorySessionImp()):
    """
    初始化 session
    """
    session: Session = Session(app, sessionImp)
    return session
