# vn.py框架的Web端管理服务器

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/vnpy-logo.png"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-1.0.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-linux|windows-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.7-blue.svg" />
    <img src ="https://img.shields.io/github/license/vnpy/vnpy.svg?color=orange"/>
</p>

## 说明

vnpy框架的web端管理服务器


## 安装

安装需要基于2.4.0版本以上的[VN Studio](https://www.vnpy.com)。

下载解压后在cmd运行：

```
python setup.py install
```

## 使用步骤

1. 运行script下的run.py
2. 点击功能下的网页端服务
3. 配置用户名、密码和SECRET_KEY,其余可默认(用户名和密码与CTP无关，可任意设定)
4. 点击启动
5. 程序会自动读取C:\Users\用户名\.vntrader\connect_ctp.json中的CTP配置
6. 打开浏览器，并访问http://127.0.0.1:8000/
7. 输入3中配置的用户名和密码，并登录
8. 后台启动完成后，会开始自动推送

## 文件功能

* tradeServer.py：基于vnpy.rpc模块实现的交易服务器，包含CTP接口模块
* webServer.py：基于Fastapi实现的Web服务器，内部通过vnpy.rpc客户端来访问交易服务器
* engine.py: 负责调用tradeServer和通过subprocess运行webServer
* run.py: 程序入口

## 架构设计

* 基于Fastapi-Restful实现的主动函数调用功能，数据流程：
	1. 用户点击浏览器中的某个按钮，发起Restful功能调用
	2. Web服务器收到Restful请求，将其转化为RPC功能调用发送给交易服务器
	3. 交易服务器收到RPC请求，执行具体的功能逻辑，并返回结果
	4. Web服务器返回Restful请求的结果给浏览器

* 基于Fastapi-Websocket实现的被动数据推送功能，数据流程：
	1. 交易服务器的事件引擎转发某个事件推送，并推送给RPC客户端（Web服务器）
	2. Web服务器收到事件推送后，将其转化为json格式，并通过Websocket发出
	3. 浏览器通过Websocket收到推送的数据，并渲染在Web前端界面上

* 将程序分为两个进程的主要原因包括：
	1. 交易服务器中的策略运行和数据计算的运算压力较大，需要保证尽可能保证低延时效率
	2. Web服务器需要面对互联网访问，将交易相关的逻辑剥离能更好保证安全性
	