""""""
import subprocess
import os
import json

from vnpy.event import EventEngine
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.rpc import RpcClient
from vnpy.gateway.ctp import CtpGateway

from vnpy_webtrader.tradeServer import WebEngine


APP_NAME = "WebTrade"

abs_name = os.path.abspath(__file__)
dir_name = os.path.dirname(abs_name)


class WebTradeEngine(BaseEngine):
    """"""
    setting_filename = "web_trade_setting.json"

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

        self.active = False

        # 设置登录所需的用户名和密码
        self.USERNAME = ""
        self.PASSWORD = ""

        # %% 预设相关参数
        # RPC连接地址
        self.REQ_ADDRESS = ""
        self.SUB_ADDRESS = ""
        # fastapi加密使用信息
        # SECRET_KEY 可用 openssl rand -hex 32 生成
        self.SECRET_KEY = ""
        self.ALGORITHM = ""
        self.ACCESS_TOKEN_EXPIRE_MINUTES = ""

    def start_trade(self, setting):
        """"""
        # 获取由widget传输的ui界面的数据
        self.USERNAME = setting["username"]
        self.PASSWORD = setting["password"]
        self.REQ_ADDRESS = setting["req_address"]
        self.SUB_ADDRESS = setting["sub_address"]
        self.SECRET_KEY = setting["secret_key"]
        self.ALGORITHM = setting["algorithm"]
        self.ACCESS_TOKEN_EXPIRE_MINUTES = setting["access_token_expire_minutes"]

        # 将参数添加到subprocess执行列表，通过sys.argv传递给子进程
        self.subprocess_execute_list = []
        self.subprocess_execute_list.append(self.USERNAME)
        self.subprocess_execute_list.append(self.PASSWORD)
        self.subprocess_execute_list.append(self.REQ_ADDRESS)
        self.subprocess_execute_list.append(self.SUB_ADDRESS)
        self.subprocess_execute_list.append(self.SECRET_KEY)
        self.subprocess_execute_list.append(self.ALGORITHM)
        self.subprocess_execute_list.append(self.ACCESS_TOKEN_EXPIRE_MINUTES)

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
        with open(os.getcwd() + "/.vntrader/connect_ctp.json", "r", encoding="utf8") as f:
            CTPSETTING = json.load(f)
        # 连接rpc，连接CTP，断开rpc
        rpc = RpcClient()
        rpc.start(self.REQ_ADDRESS, self.SUB_ADDRESS)
        rpc.connect(CTPSETTING, "CTP")
        rpc.stop()

        # web服务
        # 启动web服务器
        web_path = os.path.join(dir_name, "webServer.py")
        self.subprocess_execute_list.insert(0, web_path)
        self.subprocess_execute_list.insert(0, "python")
        subprocess.Popen(self.subprocess_execute_list)
