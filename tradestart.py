from tradeServer import WebEngine

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine

from vnpy.gateway.ctp import CtpGateway
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_backtester import CtaBacktesterApp

event_engine = EventEngine()
main_engine = MainEngine(event_engine)

main_engine.add_gateway(CtpGateway)

c = WebEngine(main_engine, event_engine)

print('启动交易服务器进程')
