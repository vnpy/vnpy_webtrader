from datetime import datetime

from vnpy.trader.constant import Direction, Exchange, Offset, OrderType, Status
from vnpy.trader.object import OrderData, PositionData

import vnpy_webtrader.web as web_api


class FakeRpcClient:
    def __init__(self, orders: list[OrderData], positions: list[PositionData]) -> None:
        self._orders: list[OrderData] = orders
        self._positions: list[PositionData] = positions

    def get_all_orders(self) -> list[OrderData]:
        return self._orders

    def get_all_positions(self) -> list[PositionData]:
        return self._positions


def test_get_all_orders_returns_handler_fields() -> None:
    order_time: datetime = datetime(2026, 10, 4, 9, 30)
    order: OrderData = OrderData(
        gateway_name="TEST",
        symbol="rb2510",
        exchange=Exchange.SHFE,
        orderid="1001",
        type=OrderType.LIMIT,
        direction=Direction.LONG,
        offset=Offset.OPEN,
        price=3510,
        volume=2,
        traded=1,
        status=Status.NOTTRADED,
        datetime=order_time,
        reference="web",
    )
    web_api.rpc_client = FakeRpcClient([order], [])

    rows: list[dict] = web_api.get_all_orders()

    assert len(rows) == 1
    row: dict = rows[0]
    assert row["gateway_name"] == "TEST"
    assert row["symbol"] == "rb2510"
    assert row["exchange"] == Exchange.SHFE.value
    assert row["orderid"] == "1001"
    assert row["vt_orderid"] == "TEST.1001"
    assert row["vt_symbol"] == "rb2510.SHFE"
    assert row["type"] == OrderType.LIMIT.value
    assert row["direction"] == Direction.LONG.value
    assert row["offset"] == Offset.OPEN.value
    assert row["price"] == 3510
    assert row["volume"] == 2
    assert row["traded"] == 1
    assert row["status"] == Status.NOTTRADED.value
    assert row["datetime"] == str(order_time)
    assert row["reference"] == "web"


def test_get_all_positions_returns_handler_fields() -> None:
    position: PositionData = PositionData(
        gateway_name="TEST",
        symbol="ag2506",
        exchange=Exchange.SHFE,
        direction=Direction.SHORT,
        volume=5,
        frozen=1,
        price=7800,
        pnl=12.5,
        yd_volume=4,
    )
    web_api.rpc_client = FakeRpcClient([], [position])

    rows: list[dict] = web_api.get_all_positions()

    assert len(rows) == 1
    row: dict = rows[0]
    assert row["gateway_name"] == "TEST"
    assert row["symbol"] == "ag2506"
    assert row["exchange"] == Exchange.SHFE.value
    assert row["direction"] == Direction.SHORT.value
    assert row["volume"] == 5
    assert row["frozen"] == 1
    assert row["price"] == 7800
    assert row["pnl"] == 12.5
    assert row["yd_volume"] == 4
    assert row["vt_symbol"] == "ag2506.SHFE"
    assert row["vt_positionid"] == position.vt_positionid
