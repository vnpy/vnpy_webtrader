import subprocess
import os
import json

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.gateway.ctp import CtpGateway
from vnpy.rpc import RpcClient

from vnpy_webtrader.tradeServer import WebEngine

# 地址处理 在将事件引擎绑定到主引擎前获取绝对地址，否则地址会发生改变
abs_name = os.path.abspath(__file__)
dir_name = os.path.dirname(abs_name)
work_path = os.path.dirname(dir_name)

# 设置登录所需的用户名和密码
USERNAME = "test"
PASSWORD = "test"

# %% 预设相关参数
# RPC连接地址
REQ_ADDRESS = "tcp://127.0.0.1:2014"
SUB_ADDRESS = "tcp://127.0.0.1:4102"

# fastapi加密使用信息
# SECRET_KEY 可用 openssl rand -hex 32 生成
SECRET_KEY = "dfd11067782d62fe888b73eca97bdb0e5b2ddb7e3e6e0fd9d88a302a9b2d0b1a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = "30"


# %% 将参数添加到subprocess执行列表，通过sys.argv传递给子进程
subprocess_execute_list = []
subprocess_execute_list.append(USERNAME)
subprocess_execute_list.append(PASSWORD)
subprocess_execute_list.append(REQ_ADDRESS)
subprocess_execute_list.append(SUB_ADDRESS)
subprocess_execute_list.append(SECRET_KEY)
subprocess_execute_list.append(ALGORITHM)
subprocess_execute_list.append(ACCESS_TOKEN_EXPIRE_MINUTES)

# %% 引擎
# 创建事件引擎
event_engine = EventEngine()
# 创建主引擎，并将事件引擎绑定到主引擎上
main_engine = MainEngine(event_engine)
# 在主引擎上添加ctp接口
main_engine.add_gateway(CtpGateway)


# %%交易服务
# 启动交易服务器
trade = WebEngine(main_engine, event_engine)
print('交易服务器启动完成')


# %% rpc
# 读取ctp登录信息
with open(work_path + "/static/CTP_connect.json", "r", encoding="utf8") as f:
    CTPSETTING = json.load(f)
# 连接rpc，连接CTP
rpc = RpcClient()
rpc.start(REQ_ADDRESS, SUB_ADDRESS)
rpc.connect(CTPSETTING, "CTP")


# %%web服务
# 启动web服务器
web_path = os.path.join(work_path, "vnpy_webtrader", "webServer.py")
subprocess_execute_list.insert(0, web_path)
subprocess_execute_list.insert(0, "python")
subprocess.run(subprocess_execute_list)
