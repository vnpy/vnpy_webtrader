import subprocess

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.gateway.ctp import CtpGateway

from vnpy_webtrader.tradeServer import WebEngine
from vnpy_webtrader.webServer import main

event_engine = EventEngine()
main_engine = MainEngine(event_engine)
main_engine.add_gateway(CtpGateway)

trade = WebEngine(main_engine, event_engine)
print('交易服务器启动完成')
web = subprocess.run(main())
