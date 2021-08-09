""""""
import sys
import subprocess
import os
import json

from PyQt5.QtWidgets import QApplication

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.gateway.ctp import CtpGateway
from vnpy.rpc import RpcClient

from vnpy_webtrader.tradeServer import WebEngine
from widget import Example

# 地址处理 在将事件引擎绑定到主引擎前获取绝对地址，否则地址会发生改变
abs_name = os.path.abspath(__file__)
dir_name = os.path.dirname(abs_name)
work_path = os.path.dirname(dir_name)
dir_path = os.path.dirname(work_path)


class START(Example):
    """"""
    def __init__(self) -> None:
        super().__init__()
        # 设置登录所需的用户名和密码
        self.USERNAME = self.username
        self.PASSWORD = self.password

        # %% 预设相关参数
        # RPC连接地址
        self.REQ_ADDRESS = self.req_address
        self.SUB_ADDRESS = self.sub_address

        # fastapi加密使用信息
        # SECRET_KEY 可用 openssl rand -hex 32 生成
        self.SECRET_KEY = self.secret_key
        self.ALGORITHM = self.algorithm
        self.ACCESS_TOKEN_EXPIRE_MINUTES = self.access_token_expire_minutes

        # %% 将参数添加到subprocess执行列表，通过sys.argv传递给子进程
        self.subprocess_execute_list = []
        self.subprocess_execute_list.append(self.USERNAME)
        self.subprocess_execute_list.append(self.PASSWORD)
        self.subprocess_execute_list.append(self.REQ_ADDRESS)
        self.subprocess_execute_list.append(self.SUB_ADDRESS)
        self.subprocess_execute_list.append(self.SECRET_KEY)
        self.subprocess_execute_list.append(self.ALGORITHM)
        self.subprocess_execute_list.append(self.ACCESS_TOKEN_EXPIRE_MINUTES)

    def login_trade(self):
        # 引擎
        # 创建事件引擎
        event_engine = EventEngine()
        # 创建主引擎，并将事件引擎绑定到主引擎上
        main_engine = MainEngine(event_engine)
        # 在主引擎上添加ctp接口
        main_engine.add_gateway(CtpGateway)

        # 启动交易服务器
        WebEngine(main_engine, event_engine)
        print('交易服务器启动完成')

        # rpc
        # 读取ctp登录信息
        with open(dir_path + "/static/CTP_connect.json", "r", encoding="utf8") as f:
            CTPSETTING = json.load(f)
        # 连接rpc，连接CTP
        rpc = RpcClient()
        rpc.start(self.REQ_ADDRESS, self.SUB_ADDRESS)
        rpc.connect(CTPSETTING, "CTP")

        # web服务
        # 启动web服务器
        web_path = os.path.join(work_path, "webServer.py")
        self.subprocess_execute_list.insert(0, web_path)
        self.subprocess_execute_list.insert(0, "python")
        subprocess.Popen(self.subprocess_execute_list)


if __name__ == "__main__":
    """"""
    app = QApplication(sys.argv)
    ex = START()
    sys.exit(app.exec_())
