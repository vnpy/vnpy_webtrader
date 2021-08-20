import sys
from time import sleep
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_binance import BinanceUsdtGateway
from vnpy.trader.ui import QtCore
from vnpy_webtrader import WebTraderApp
setting = {
    "req_address": 'tcp://127.0.0.1:2014',
    "sub_address": 'tcp://127.0.0.1:4102'
}
binances_setting = {
    "key": "",
    "secret": "",
    "会话数": 3,
    "服务器": "REAL",
    "合约模式": "正向",
    "代理地址": "",
    "代理端口": 0,
}
def main():

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(BinanceUsdtGateway)
    # main_engine.connect(binances_setting, "BINANCE_USDT")
    web_engine = main_engine.add_app(WebTraderApp)

    web_engine.start_server(setting['req_address'], setting['sub_address'])
    cmd = [
        "-m"
        "uvicorn",
        "vnpy_webtrader.web:app",
        "--reload"
    ]
    process = QtCore.QProcess()
    process.setWorkingDirectory("../")
    process.start(sys.executable, cmd)

    while True:
        sleep(10)

if __name__ == "__main__":
    main()
