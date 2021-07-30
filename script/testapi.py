import json
import time
from datetime import timedelta, datetime

from jose import jwt

from vnpy.api.rest import RestClient
from vnpy.api.websocket import WebsocketClient

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = "dfd11067782d62fe888b73eca97bdb0e5b2ddb7e3e6e0fd9d88a302a9b2d0b1a"
data = {"sub": "test"}
access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
expire = datetime.utcnow() + access_token_expires
to_encode = data.copy()
to_encode.update({"exp": expire})
encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

rest = RestClient()
webso = WebsocketClient()

webso.init('ws://127.0.0.1:8000/ws/')
webso.start()


def show(a, b):
    print(a)


rest.init("http://127.0.0.1:8000")
# rest.add_request("get","/", dict, headers={"accept": "application/json"})
rest.add_request("post", "/token", show, data={"username": "test", "password": "test"}, headers={"accept": "application/json"})
rest.add_request("get", "/connect", show, headers={"accept": "application/json", "Authorization": "Bearer " + encoded_jwt})
rest.add_request("post", "/send_order", show, data=json.dumps({
    "symbol": "eb2110",
    "exchange": "DCE",
    "direction": "多",
    "type": "限价",
    "volume": "1.0",
    "price": "9030.0",
    "offset": "开",
    "reference": ""
    }), headers={"accept": "application/json", "Authorization": "Bearer " + encoded_jwt, "Content-Type": "application/json"})

rest.add_request("post", "/cancel_order", show, data=json.dumps({
    "orderid": "3_1277016586_1",
    "symbol": "eb2110",
    "exchange": "DCE"
    }), headers={"accept": "application/json", "Authorization": "Bearer " + encoded_jwt})

rest.add_request("post", "/account", show, data=json.dumps({
    "vt_accountid": "CTP.189672"
    }), headers={"accept": "application/json", "Authorization": "Bearer " + encoded_jwt})

rest.start()


# 等待10秒，等待连接成功数据跳动之后，否则无法查询数据
time.sleep(10)

rest.add_request("post", "/query_order", show, data=json.dumps({
    "vt_orderid": "CTP.3_1438961297_2"
    }), headers={"accept": "application/json", "Authorization": "Bearer " + encoded_jwt})

rest.add_request("post", "/trade", show, data=json.dumps({
    "vt_tradeid": "CTP.       95574"
    }), headers={"accept": "application/json", "Authorization": "Bearer " + encoded_jwt, "Content-Type": "application/json"})

rest.add_request("post", "/position", show, data=json.dumps({
    "vt_positionid": "eb2110.DCE.多"
    }), headers={"accept": "application/json", "Authorization": "Bearer " + encoded_jwt})

rest.add_request("post", "/contract", show, data=json.dumps({
    "vt_symbol": "eb2110.DCE"
    }), headers={"accept": "application/json", "Authorization": "Bearer " + encoded_jwt})

rest.start()
