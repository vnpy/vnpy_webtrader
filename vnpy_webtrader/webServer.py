""""""
from typing import Any, List, Optional
import json
import asyncio
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
REQ_ADDRESS = 'tcp://127.0.0.1:2014'
SUB_ADDRESS = 'tcp://127.0.0.1:4102'

# %% fastapi加密与授权
# 加密使用信息
# SECRET_KEY 可用 openssl rand -hex 32 生成
SECRET_KEY = "dfd11067782d62fe888b73eca97bdb0e5b2ddb7e3e6e0fd9d88a302a9b2d0b1a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# 实例化CryptContext用于处理哈希密码
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# fastapi授权
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# %% 读取本地登录信息与静态页面
# 读取web登录信息
with open("vnpy_webtrader/Web_setting.json", "r", encoding="utf8") as f:
    WEBSETTING = json.load(f)
    USERNAME = WEBSETTING["username"]
    PASSWORD = WEBSETTING["password"]
# 读取ctp登录信息
with open("vnpy_webtrader/CTP_connect.json", "r", encoding="utf8") as f:
    CTPSETTING = json.load(f)
# 获取静态页面
with open("static/index.html") as f:
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


class QOrder(BaseModel):
    """"""
    # gateway_name: str
    # orderid: str
    vt_orderid : str


class QTrade(BaseModel):
    """"""
    # gateway_name: str
    # tradeid: str
    vt_tradeid : str


class QPosition(BaseModel):
    """"""
    # vt_symbol: str
    # direction: str
    vt_positionid : str


class QAccount(BaseModel):
    """"""
    # gateway_name: str
    # accountid: str
    vt_accountid : str


class QContract(BaseModel):
    """"""
    # symbol: str
    # exchange: str
    vt_symbol : str


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


def get_access(token: str = Depends(oauth2_scheme)):
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
async def get():
    """获取主页面"""
    return HTMLResponse(index)


# token验证
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
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
@app.get("/connect")
async def connect_to_trade_server(token: str = Depends(oauth2_scheme)):
    """连接"""
    get_access(token)
    rpc.connect(CTPSETTING, "CTP")


# 发送订单
@app.post("/send_order")
async def send_order(order: Order, token: str = Depends(oauth2_scheme)):
    """"""
    get_access(token)
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
    return tmp


# 取消订单
@app.post("/cancel_order")
async def cancel_order(cq: CRequest, token: str = Depends(oauth2_scheme)):
    """"""
    get_access(token)
    data = CancelRequest(cq.orderid, cq.symbol, Exchange(cq.exchange))
    tmp = rpc.cancel_order(data, "CTP")
    return tmp


# 查询订单
@app.post("/query_order")
async def query_order(qorder: QOrder, token: str = Depends(oauth2_scheme)):
    """"""
    get_access(token)
    # vt_orderid = f"{qorder.gateway_name}.{qorder.orderid}"
    vt_orderid = qorder.vt_orderid
    tmp = rpc.get_order(vt_orderid)
    return tmp


# 查询交易
@app.post("/trade")
async def query_trade(qtrade: QTrade, token: str = Depends(oauth2_scheme)):
    """"""
    get_access(token)
    # vt_tradeid = f"{qtrade.gateway_name}.{qtrade.tradeid}"
    vt_tradeid = qtrade.vt_tradeid
    tmp = rpc.get_trade(vt_tradeid)
    return tmp


# 查询持仓
@app.post("/position")
async def query_position(qposition: QPosition, token: str = Depends(oauth2_scheme)):
    """"""
    get_access(token)
    # vt_positionid = f"{qposition.vt_symbol}.{qposition.direction}"
    vt_positionid = qposition.vt_positionid
    tmp = rpc.get_position(vt_positionid)
    return tmp


# 查询账户
@app.post("/account")
async def query_account(qaccount: QAccount, token: str = Depends(oauth2_scheme)):
    """"""
    get_access(token)
    # vt_accountid = f"{qaccount.gateway_name}.{qaccount.accountid}"
    vt_accountid = qaccount.vt_accountid
    tmp = rpc.get_account(vt_accountid)
    return tmp


# 查询合约
@app.post("/contract")
async def query_contract(qcontract: QContract, token: str = Depends(oauth2_scheme)):
    """"""
    get_access(token)
    # vt_symbol = f"{qcontract.symbol}.{qcontract.exchange}"
    vt_symbol = qcontract.vt_symbol
    tmp = rpc.get_contract(vt_symbol)
    return tmp


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
    print("websock", data.__dict__)
    asyncio.run_coroutine_threadsafe(manager.broadcast(str(data)), _loop)


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
