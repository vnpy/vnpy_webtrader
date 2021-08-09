""""""
from collections import defaultdict

from vnpy.trader.object import OrderRequest, LogData
from vnpy.event import Event, EventEngine, EVENT_TIMER
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.event import EVENT_TRADE, EVENT_ORDER, EVENT_LOG
from vnpy.trader.constant import Status
from vnpy.trader.utility import load_json, save_json
from tradeServer import WebEngine


APP_NAME = "WebTrade"


class WebTradeEngine(BaseEngine):
    """"""
    setting_filename = "web_trade_setting.json"

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

        self.active = False

        # 设置登录所需的用户名和密码
        self.USERNAME = "test"
        self.PASSWORD = "test"

        # %% 预设相关参数
        # RPC连接地址
        self.REQ_ADDRESS = "tcp://127.0.0.1:2014"
        self.SUB_ADDRESS = "tcp://127.0.0.1:4102"
        # fastapi加密使用信息
        # SECRET_KEY 可用 openssl rand -hex 32 生成
        self.SECRET_KEY = "dfd11067782d62fe888b73eca97bdb0e5b2ddb7e3e6e0fd9d88a302a9b2d0b1a"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = "30"

        # %% 将参数添加到subprocess执行列表，通过sys.argv传递给子进程
        self.subprocess_execute_list = []
        self.subprocess_execute_list.append(self.USERNAME)
        self.subprocess_execute_list.append(self.PASSWORD)
        self.subprocess_execute_list.append(self.REQ_ADDRESS)
        self.subprocess_execute_list.append(self.SUB_ADDRESS)
        self.subprocess_execute_list.append(self.SECRET_KEY)
        self.subprocess_execute_list.append(self.ALGORITHM)
        self.subprocess_execute_list.append(self.ACCESS_TOKEN_EXPIRE_MINUTES)

    def start_trade(self):
        # 启动交易服务器
        WebEngine(main_engine, event_engine)
        print('交易服务器启动完成')

        # web服务
        # 启动web服务器
        web_path = os.path.join(work_path, "webServer.py")
        self.subprocess_execute_list.insert(0, web_path)
        self.subprocess_execute_list.insert(0, "python")
        subprocess.Popen(self.subprocess_execute_list)
