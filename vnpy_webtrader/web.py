from enum import Enum
from typing import Any, List, Optional
import asyncio
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext

from vnpy.rpc import RpcClient
from vnpy.trader.object import (
    AccountData,
    ContractData,
    OrderData,
    OrderRequest,
    PositionData,
    SubscribeRequest,
    TickData,
    TradeData
)
from vnpy.trader.constant import (
    Exchange,
    Direction,
    OrderType,
    Offset,
)
from vnpy.trader.utility import load_json, get_file_path


# Web服务运行配置
SETTING_FILENAME = "web_trader_setting.json"
SETTING_FILEPATH = get_file_path(SETTING_FILENAME)

setting = load_json(SETTING_FILEPATH)
USERNAME = setting["username"]              # 用户名
PASSWORD = setting["password"]              # 密码
REQ_ADDRESS = setting["req_address"]        # 请求服务地址
SUB_ADDRESS = setting["sub_address"]        # 订阅服务地址


SECRET_KEY = "test"                     # 数据加密密钥
ALGORITHM = "HS256"                     # 加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30        # 令牌超时（分钟）


# 实例化CryptContext用于处理哈希密码
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# fastapi授权
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


rpc_client: RpcClient = None


def to_dict(o: dataclass) -> dict:
    """将对象转换为字典"""
    data = {}
    for k, v in o.__dict__.items():
        if isinstance(v, Enum):
            data[k] = v.value
        elif isinstance(v, datetime):
            data[k] = str(v)
        else:
            data[k] = v
    return data


class Token(BaseModel):
    """令牌数据"""
    access_token: str
    token_type: str


def authenticate_user(current_username: str, username: str, password: str):
    """校验用户"""
    web_username = current_username
    hashed_password = pwd_context.hash(PASSWORD)

    if web_username != username:
        return False

    if not pwd_context.verify(password, hashed_password):
        return False

    return username


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_access(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    if username != USERNAME:
        raise credentials_exception
    return True


# 创建FastAPI应用
app = FastAPI()


@app.get("/")
def index() -> HTMLResponse:
    """获取主页面"""
    abs_name = os.path.abspath(__file__)
    dir_name = os.path.dirname(abs_name)

    index_path = os.path.dirname(dir_name) + "/vnpy_webtrader/static/index.html"
    with open(index_path) as f:
        content = f.read()

    return HTMLResponse(content)


@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    web_username = authenticate_user(USERNAME, form_data.username, form_data.password)
    if not web_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": web_username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tick/{vt_symbol}")
def subscribe(vt_symbol: str, access: bool = Depends(get_access)) -> None:
    """订阅行情"""
    if not access:
        return "Not authenticated"

    contract: ContractData = rpc_client.get_contract(vt_symbol)
    if not contract:
        return f"找不到合约{vt_symbol}"

    req = SubscribeRequest(contract.symbol, contract.exchange)
    rpc_client.subscribe(req, contract.gateway_name)


@app.get("/tick")
def get_all_ticks(access: bool = Depends(get_access)) -> list:
    """查询行情信息"""
    if not access:
        return "Not authenticated"

    ticks: List[TickData] = rpc_client.get_all_ticks()
    return [to_dict(tick) for tick in ticks]


class OrderRequestModel(BaseModel):
    """委托请求模型"""
    symbol: str
    exchange: Exchange
    direction: Direction
    type: OrderType
    volume: float
    price: float = 0
    offset: Offset = Offset.NONE
    reference: str = ""


@app.post("/order")
def send_order(model: OrderRequestModel, access: bool = Depends(get_access)) -> str:
    """委托下单"""
    if not access:
        return "Not authenticated"

    req: OrderRequest = OrderRequest(**model.__dict__)

    contract: ContractData = rpc_client.get_contract(req.vt_symbol)
    if not contract:
        return f"找不到合约{req.symbol} {req.exchange.value}"

    vt_orderid: str = rpc_client.send_order(req, contract.gateway_name)
    return vt_orderid


@app.delete("/order/{vt_orderid}")
def cancel_order(vt_orderid: str, access: bool = Depends(get_access)) -> None:
    """委托撤单"""
    if not access:
        return "Not authenticated"

    order: OrderData = rpc_client.get_order(vt_orderid)
    if not order:
        return f"找不到委托{vt_orderid}"

    req = order.create_cancel_request()
    rpc_client.cancel_order(req, order.gateway_name)


@app.get("/order")
def get_all_orders(access: bool = Depends(get_access)) -> list:
    """查询委托信息"""
    if not access:
        return "Not authenticated"

    orders: OrderData = rpc_client.get_all_orders()
    return [to_dict(order) for order in orders]


@app.get("/trade")
def get_all_trades(access: bool = Depends(get_access)) -> list:
    """查询成交信息"""
    if not access:
        return "Not authenticated"

    trades: List[TradeData] = rpc_client.get_all_trades()
    return [to_dict(trade) for trade in trades]


@app.get("/position")
def get_all_positions(access: bool = Depends(get_access)) -> list:
    """查询持仓信息"""
    if not access:
        return "Not authenticated"

    positions: List[PositionData] = rpc_client.get_all_positions()
    return [to_dict(position) for position in positions]


@app.get("/account")
def get_all_accounts(access: bool = Depends(get_access)) -> list:
    """查询账户资金"""
    if not access:
        return "Not authenticated"

    accounts: List[AccountData] = rpc_client.get_all_accounts()
    return [to_dict(account) for account in accounts]


@app.get("/contract")
def get_all_contracts(access: bool = Depends(get_access)) -> list:
    """查询合约信息"""
    if not access:
        return "Not authenticated"

    contracts: List[ContractData] = rpc_client.get_all_contracts()
    return [to_dict(contract) for contract in contracts]


active_websockets: List[WebSocket] = []
event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()


# websocket传递数据
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Weboskcet连接处理"""
    await websocket.accept()
    active_websockets.append(websocket)

    print("websocket connected")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_websockets.remove(websocket)


async def websocket_broadcast(msg: str) -> None:
    """Websocket数据广播"""
    for websocket in active_websockets:
        await websocket.send_text(msg)


def rpc_callback(topic: str, data: Any):
    """RPC回调函数"""
    if not active_websockets:
        return

    data = {
        "topic": topic,
        "data": to_dict(data)
    }
    msg: str = json.dumps(data, ensure_ascii=False)
    asyncio.run_coroutine_threadsafe(websocket_broadcast(msg), event_loop)


@app.on_event("startup")
def startup_event() -> None:
    """应用启动事件"""
    global rpc_client
    rpc_client = RpcClient()
    rpc_client.callback = rpc_callback
    rpc_client.subscribe_topic("")
    rpc_client.start(REQ_ADDRESS, SUB_ADDRESS)


@app.on_event("shutdown")
def shutdown_event() -> None:
    """应用停止事件"""
    print("rpc_client exit")
    rpc_client.stop()
