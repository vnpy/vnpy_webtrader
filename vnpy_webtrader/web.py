from enum import Enum
from typing import Any, List, Optional
import asyncio
import sys
import os
from datetime import datetime, timedelta
from dataclasses import dataclass

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
import uvicorn

from vnpy.rpc import RpcClient
from vnpy.trader.object import AccountData, ContractData, OrderData, OrderRequest, CancelRequest, Exchange, Direction, OrderType, Offset, PositionData, TradeData

# Web服务运行配置
# USERNAME = sys.argv[1]              # 用户名
# PASSWORD = sys.argv[2]              # 密码
# REQ_ADDRESS = sys.argv[3]           # 请求服务地址
# SUB_ADDRESS = sys.argv[4]           # 订阅服务地址

USERNAME = "test"                       # 用户名
PASSWORD = "test"                       # 密码
REQ_ADDRESS = "tcp://127.0.0.1:2014"    # 请求服务地址
SUB_ADDRESS = "tcp://127.0.0.1:4102"    # 订阅服务地址
SECRET_KEY = "test"                     # 数据加密密钥
ALGORITHM = "HS256"                     # 加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30        # 令牌超时（分钟）


# 实例化CryptContext用于处理哈希密码
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# fastapi授权
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


rpc_client = RpcClient()

# fastapi使用请求体
class Token(BaseModel):
    """"""
    access_token: str
    token_type: str



class OrderRequestModel(BaseModel):
    """委托请求"""
    symbol: str
    exchange: Exchange
    direction: Direction
    type: OrderType
    volume: float
    price: float = 0
    offset: Offset = Offset.NONE
    reference: str = ""

    


# fastapi加密函数
def verify_password(plain_password, hashed_password):
    """"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """"""
    return pwd_context.hash(password)


def authenticate_user(current_username, username: str, password: str):
    """"""
    web_username = current_username
    hashed_password = get_password_hash(PASSWORD)
    if web_username != username:
        return False
    if not verify_password(password, hashed_password):
        return False
    return username


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """"""
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
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """"""
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
def query_order(access: bool = Depends(get_access)) -> list:
    """查询委托信息"""
    if not access:
        return "Not authenticated"

    orders: OrderData = rpc_client.get_all_trades()
    return [to_dict(order) for order in orders]


@app.get("/trade")
def query_trade(access: bool = Depends(get_access)) -> list:
    """查询成交信息"""
    if not access:
        return "Not authenticated"
    
    trades: List[TradeData] = rpc_client.get_all_trades()
    return [to_dict(trade) for trade in trades]


@app.get("/position")
def query_position(access: bool = Depends(get_access)) -> list:
    """查询持仓信息"""
    if not access:
        return "Not authenticated"
    
    positions: List[PositionData] = rpc_client.get_all_positions()
    return [to_dict(position) for position in positions]


@app.get("/account")
def query_account(access: bool = Depends(get_access)) -> list:
    """查询账户资金"""
    if not access:
        return "Not authenticated"
    
    accounts: List[AccountData] = rpc_client.get_all_accounts()
    return [to_dict(account) for account in accounts]


@app.get("/contract")
def query_contract(access: bool = Depends(get_access)) -> list:
    """查询合约信息"""
    if not access:
        return "Not authenticated"
    print(1)
    contracts: List[ContractData] = rpc_client.get_all_contracts()
    print(2)
    return [to_dict(contract) for contract in contracts]


# # websocket内容
# # 创建websocket管理对象
# class ConnectionManager:
#     """"""
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)


# # 实例化websocket管理对象
# manager = ConnectionManager()
# # 用于接收当前页面连接的websocket
# individual_websocket = ""
# # _loop全局变量用于接收websocket内循环
# _loop = ""


# # websocket传递数据
# @app.websocket("/ws/")
# async def websocket_endpoint(websocket: WebSocket):
#     """"""
#     await manager.connect(websocket)
#     global individual_websocket, _loop
#     individual_websocket = websocket
#     print("websocket connected")
#     try:
#         while True:
#             _loop = asyncio.get_event_loop()
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)


# 回调函数用于接受rpc_client提供的数据并传递给websocket
def calldata(topic: str, data: Any):
    """"""
    return
    global individual_websocket, _loop, manager
    print(f"websocket-{topic}-{data}")
    try:
        broadcast_data = f"{topic}-{data.__dict__}"
        asyncio.run_coroutine_threadsafe(manager.broadcast(str(broadcast_data)), _loop)
    except AttributeError:
        print("please connect to webstocket")


# 添加回调函数
rpc_client.callback = calldata


# @app.on_event("shutdown")
# def shutdown_event():
#     print("rpc_client exit")
#     rpc_client.stop()


def to_dict(o: dataclass) -> dict:
    """将对象转换为字典"""
    data = {}
    for k, v in o.__dict__.items():
        if isinstance(v, Enum):
            data[k] = v.value
        else:
            data[k] = v
    return data


rpc_client.subscribe_topic("")
rpc_client.start(REQ_ADDRESS, SUB_ADDRESS)


# 主运行函数
def main():
    """"""
    global rpc_client
    rpc_client.subscribe_topic("")
    rpc_client.start(REQ_ADDRESS, SUB_ADDRESS)

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
