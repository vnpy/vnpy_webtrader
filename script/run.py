import subprocess

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.gateway.ctp import CtpGateway

from vnpy_webtrader.tradeServer import WebEngine
from vnpy_webtrader.webServer import main

# 创建事件引擎
event_engine = EventEngine()
# 创建主引擎，并将事件引擎绑定到主引擎上
main_engine = MainEngine(event_engine)
# 在主引擎上添加ctp接口
main_engine.add_gateway(CtpGateway)

# 启动交易服务器
trade = WebEngine(main_engine, event_engine)
print('交易服务器启动完成')
# 启动web服务器
web = subprocess.run(main())
