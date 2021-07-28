""""""
from vnpy.rpc import RpcServer
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.event import (
    EVENT_TICK,
    EVENT_ORDER,
    EVENT_TRADE,
    EVENT_POSITION,
    EVENT_ACCOUNT
)
from vnpy.event import EventEngine, Event
from vnpy.trader.object import (
    AccountData,
    PositionData,
    TickData,
    TradeData,
    OrderData,
)

APP_NAME = "RpcService"


class WebEngine(BaseEngine):
    """"""
    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)
        self.server = RpcServer()

        self.rep_address = "tcp://127.0.0.1:2014"
        self.pub_address = "tcp://127.0.0.1:4102"
        self.server.start(self.rep_address, self.pub_address)

        self.init_serve()
        self.register_event()

    def init_serve(self):
        """"""
        self.server.register(self.main_engine.connect)
        self.server.register(self.main_engine.send_order)
        self.server.register(self.main_engine.cancel_order)

        self.server.register(self.main_engine.get_order)
        self.server.register(self.main_engine.get_trade)
        self.server.register(self.main_engine.get_position)
        self.server.register(self.main_engine.get_account)
        self.server.register(self.main_engine.get_contract)

    def register_event(self) -> None:
        """
        Register event handler.
        """
        self.event_engine.register(EVENT_TICK, self.on_tick)
        self.event_engine.register(EVENT_TRADE, self.on_trade)
        self.event_engine.register(EVENT_ORDER, self.on_order)
        self.event_engine.register(EVENT_POSITION, self.on_position)
        self.event_engine.register(EVENT_ACCOUNT, self.on_account)

    def on_tick(self, event: Event) -> None:
        tick: TickData = event.data
        self.server.publish("tick", tick)
        print("tick")

    def on_trade(self, event: Event) -> None:
        trade: TradeData = event.data
        self.server.publish("trade", trade)
        print("trade")

    def on_order(self, event: Event) -> None:
        order: OrderData = event.data
        self.server.publish("order", order)
        print("order")

    def on_position(self, event: Event) -> None:
        position: PositionData = event.data
        self.server.publish("position", position)
        print("position")

    def on_account(self, event: Event) -> None:
        account: AccountData = event.data
        self.server.publish("account", account)
        print("account")

    def close(self):
        """"""
        self.server.stop()
        self.server.join()
