""""""
from typing import Any, List, Optional
import json
import asyncio
import sys
import os
from datetime import datetime, timedelta

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
import uvicorn

from vnpy.rpc import RpcClient
from vnpy.trader.object import OrderRequest, CancelRequest, Exchange, Direction, OrderType, Offset

# %% rpc
# 创建RPC对象
rpc = RpcClient()
# RPC连接地址
REQ_ADDRESS = sys.argv[1]
SUB_ADDRESS = sys.argv[2]

# %% fastapi加密与授权
# 加密使用信息
# SECRET_KEY 可用 openssl rand -hex 32 生成
SECRET_KEY = sys.argv[3]
ALGORITHM = sys.argv[4]
ACCESS_TOKEN_EXPIRE_MINUTES = int(sys.argv[5])
# 实例化CryptContext用于处理哈希密码
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# fastapi授权
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# %% 读取本地登录信息与静态页面
# 读取web登录信息
abs_name = os.path.abspath(__file__)
dir_name = os.path.dirname(abs_name)
with open(dir_name + "/Web_setting.json", "r", encoding="utf8") as f:
    WEBSETTING = json.load(f)
    USERNAME = WEBSETTING["username"]
    PASSWORD = WEBSETTING["password"]
# 读取ctp登录信息
# with open(dir_name + "/CTP_connect.json", "r", encoding="utf8") as f:
#     CTPSETTING = json.load(f)
# 获取静态页面
index_path = os.path.dirname(dir_name) + "/static/index.html"
with open(index_path) as f:
    index = f.read()


# %% fastapi使用请求体
class Token(BaseModel):
    """"""
    access_token: str
    token_type: str


class Setting(BaseModel):
    """"""
    userid: str
    password: str
    brokerid: str
    td_address: str
    md_address: str
    appid: str
    auth_code: str


class Order(BaseModel):
    """"""
    symbol: str
    exchange: Exchange
    direction: Direction
    type: OrderType
    volume: float
    price: float = 0
    offset: Offset = Offset.NONE
    reference: str = ""


class CRequest(BaseModel):
    """"""
    orderid: str
    symbol: str
    exchange: str


# %% fastapi加密函数
def verify_password(plain_password, hashed_password):
    """"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """"""
    return pwd_context.hash(password)


def authenticate_user(web_setting, username: str, password: str):
    """"""
    web_username = web_setting["username"]
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


# %% fastapi内容
# 创建fastapi对象
app = FastAPI()
# 允许所有跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 主页面
@app.get("/")
def get():
    """获取主页面"""
    return HTMLResponse(index)


# token验证
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """"""
    web_username = authenticate_user(WEBSETTING, form_data.username, form_data.password)
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


# 连接交易服务器
# @app.get("/connect")
# async def connect_to_trade_server(access: bool = Depends(get_access)):
#     """连接"""
#     if not access:
#         return "Not authenticated"
#     rpc.connect(CTPSETTING, "CTP")


# 发送订单
@app.post("/send_order")
def send_order(order: Order, access: bool = Depends(get_access)):
    """"""
    if not access:
        return "Not authenticated"
    data = OrderRequest(
        order.symbol,
        Exchange(order.exchange),
        order.direction,
        order.type,
        order.volume,
        order.price,
        order.offset,
        order.reference
        )
    tmp = rpc.send_order(data, "CTP")
    return tmp


# 取消订单
@app.post("/cancel_order")
def cancel_order(cq: CRequest, access: bool = Depends(get_access)):
    """"""
    if not access:
        return "Not authenticated"
    data = CancelRequest(cq.orderid, cq.symbol, Exchange(cq.exchange))
    tmp = rpc.cancel_order(data, "CTP")
    return tmp


# 查询订单
@app.get("/order")
def query_order(access: bool = Depends(get_access)):
    """"""
    if not access:
        return "Not authenticated"
    tmp = rpc.get_all_orders()
    if tmp is None:
        return("order cannnot be got now")

    results = {}
    for i in tmp:
        item = i
        item = item.__dict__
        item["exchange"] = item["exchange"].value
        item["type"] = item["type"].value
        item["direction"] = item["direction"].value
        item["offset"] = item["offset"].value
        item["status"] = item["status"].value
        item["datetime"] = item["datetime"].strftime("%Y-%m-%d %H:%M:%S")
        results[item["orderid"]] = item
    print(results)
    return results


# 查询交易
@app.get("/trade")
def query_trade(access: bool = Depends(get_access)):
    """"""
    if not access:
        return "Not authenticated"
    tmp = rpc.get_all_trades()
    if tmp is None:
        return("trade cannnot be got now")

    results = {}
    for i in tmp:
        item = i
        item = item.__dict__
        item["exchange"] = item["exchange"].value
        item["direction"] = item["direction"].value
        item["offset"] = item["offset"].value
        item["datetime"] = item["datetime"].strftime("%Y-%m-%d %H:%M:%S")
        results[item["tradeid"]] = item
    print(results)
    return results


# 查询持仓
@app.get("/position")
def query_position(access: bool = Depends(get_access)):
    """"""
    if not access:
        return "Not authenticated"
    tmp = rpc.get_all_positions()
    if tmp is None:
        return("position cannnot be got now")

    results = {}
    for i in tmp:
        item = i
        item = item.__dict__
        item["exchange"] = item["exchange"].value
        item["direction"] = item["direction"].value
        results[item["vt_positionid"]] = item
    print(results)
    return results


# 查询账户
@app.get("/account")
def query_account(access: bool = Depends(get_access)):
    """"""
    if not access:
        return "Not authenticated"
    tmp = rpc.get_all_accounts()
    if tmp is None:
        return("contract cannnot be got now")

    print(tmp)
    return tmp


# 查询合约
@app.get("/contract")
def query_contract(access: bool = Depends(get_access)):
    """"""
    if not access:
        return "Not authenticated"
    tmp = rpc.get_all_contracts()
    if tmp is None:
        return("contract cannnot be got now")

    results = {}
    for i in tmp[0:100]:
        item = i
        item = item.__dict__
        item["exchange"] = item["exchange"].value
        item["product"] = item["product"].value
        results[item["symbol"]] = item
    print(results)
    return results


# %% websocket内容
# 创建websocket管理对象
class ConnectionManager:
    """"""
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


# 实例化websocket管理对象
manager = ConnectionManager()
# 用于接收当前页面连接的websocket
individual_websocket = ""
# _loop全局变量用于接收websocket内循环
_loop = ""


# websocket传递数据
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    """"""
    await manager.connect(websocket)
    global individual_websocket, _loop
    individual_websocket = websocket
    print("websocket connected")
    try:
        while True:
            _loop = asyncio.get_event_loop()
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# 回调函数用于接受rpc提供的数据并传递给websocket
def calldata(topic: str, data: Any):
    """"""
    global individual_websocket, _loop, manager
    print(f"websocket-{topic}-{data}")
    try:
        broadcast_data = f"{topic}-{data.__dict__}"
        asyncio.run_coroutine_threadsafe(manager.broadcast(str(broadcast_data)), _loop)
    except AttributeError:
        print("please connect to webstocket")


# 添加回调函数
rpc.callback = calldata


# %% 主运行函数
def main():
    """"""
    global rpc
    rpc.subscribe_topic("")
    rpc.start(REQ_ADDRESS, SUB_ADDRESS)

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
