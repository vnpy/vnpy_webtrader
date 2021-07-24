from datetime import datetime
from time import sleep
from typing import Any, List
import json
import asyncio
import threading

import websockets

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Path, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from vnpy.rpc import RpcClient
from vnpy.trader.object import OrderRequest, CancelRequest, SubscribeRequest
from vnpy.trader.object import Exchange, Direction, OrderType, CancelRequest, Offset

REQ_ADDRESS = 'tcp://127.0.0.1:2014'
SUB_ADDRESS = 'tcp://127.0.0.1:4102'

# 创建fastapi对象
app = FastAPI()
# 创建RPC对象
rpc = RpcClient()
# 创建websocket管理对象
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

DD = ""

# 允许所有跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("./index.html") as f:
    index = f.read()

# 主页面
@app.get("/")
async def get():
    """获取主页面"""
    return HTMLResponse(index)

# 连接
class Setting(BaseModel):
    userid: str
    password: str 
    brokerid: str 
    td_address: str
    md_address: str 
    appid: str 
    auth_code: str


@app.get("/connect")
async def get_connect():
    """"""
    setting = {
    "用户名": "158995",
    "密码": "#Hrnmm1234",
    "经纪商代码": "9999",
    "交易服务器": "180.168.146.187:10130",
    "行情服务器": "180.168.146.187:10131",
    "产品名称": "simnow_client_test",
    "授权编码": "0000000000000000"
    }
    tmp = rpc.connect(setting, "CTP")
    return ("return: ", tmp)

    # "用户名": "189672",
    # "密码": "#gyf123456",
    

@app.post("/connect")
async def post_connect(setting: Setting):
    """"""
    tmp = {
        "用户名": setting.userid,
        "密码": setting.password,
        "经纪商代码": setting.brokerid,
        "交易服务器": setting.td_address,
        "行情服务器": setting.md_address,
        "产品名称": setting.appid,
        "授权编码": setting.auth_code
    }
    tmp = rpc.connect(tmp, "CTP")
    return ("return: ", tmp)

# 发送订单
class Order(BaseModel):
    symbol: str
    exchange: Exchange
    direction: Direction
    type: OrderType
    volume: float
    price: float = 0
    offset: Offset = Offset.NONE
    reference: str = ""


@app.get("/send_order")
async def get_send_order():
    """"""
    data = OrderRequest("60000", Exchange("SHFE"), Direction("多"), OrderType("询价"), 100.0)
    tmp = rpc.send_order(data, "CTP")
    return ("return: ", tmp)


@app.post("/send_order")
async def post_send_order(order:Order):
    """"""
    data = OrderRequest(
        order.symbol,
        order.exchange,
        order.direction,
        order.type,
        order.volume,
        order.price,
        order.offset,
        order.reference
        )
    tmp = rpc.send_order(data, "CTP")
    return ("return: ", tmp)


# 取消订单
class CRequest(BaseModel):
    orderid: str
    symbol: str
    exchange: Exchange


@app.get("/cancel_order")
async def get_cannel_order():
    """"""
    data = CancelRequest("3_-1041318151_2", "60000",  Exchange("SHFE"))
    tmp = rpc.cancel_order(data, "CTP")
    return ("return: ", tmp)

@app.post("/cancel_order")
async def post_cannel_order(cq:CRequest):
    """"""
    data = CancelRequest(cq.orderid, cq.symbol, cq.exchange)
    tmp = rpc.cancel_order(data, "CTP")
    return ("return: ", tmp)


# 查询订单
@app.get("/query_order")
async def get_query_order():
    """"""
    tmp = rpc.get_order("aaa")
    return ("return: ", tmp)


# 查询交易
@app.get("/trade")
async def get_trade():
    """"""
    tmp = rpc.get_trade("aaa")
    return ("return: ", tmp)


# 查询持仓
@app.get("/position")
async def get_position():
    """"""
    tmp = rpc.get_position("aaa")
    return ("return: ", tmp)


# 查询账户
@app.get("/account")
async def get_account(vt_accountid = Query(...)):
    """"""
    tmp = rpc.get_account(vt_accountid)
    return ("return: ", tmp)


# 查询合约
@app.get("/contract")
async def get_contract(vt_symbol = Query(...)):
    """"""
    tmp = rpc.get_contract(vt_symbol)
    return ("return: ", tmp)


_loop = ""

@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    global DD, _loop
    DD = websocket
    print("websocket connected")
    try:
        while True:
            _loop = asyncio.get_event_loop()
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def calldata(topic: str, data:Any):
    global DD, _loop, manager
    rpcdata = [topic, data]
    print(rpcdata)
    asyncio.run_coroutine_threadsafe(manager.broadcast(str(rpcdata)), _loop)

rpc.callback = calldata


def main():
    global rpc
    rpc.subscribe_topic("")
    rpc.start(REQ_ADDRESS, SUB_ADDRESS)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
