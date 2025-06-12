# VeighNa框架的Web服务模块

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/vnpy-logo.png"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-1.1.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.10|3.11|3.12|3.13-blue.svg" />
    <img src ="https://img.shields.io/github/license/vnpy/vnpy.svg?color=orange"/>
</p>

## 说明

针对B-S架构需求设计的Web服务应用模块，实现了提供主动函数调用（REST）和被动数据推送（Websocket）的Web服务器。

目前仅提供了基础的交易和管理接口，用户根据自己的需求扩展支持其他VeighNa应用模块的Web接口（如CTA策略自动交易等）。

## 安装

安装环境推荐基于4.0.0版本以上的【[**VeighNa Studio**](https://www.vnpy.com)】。

直接使用pip命令：

```
pip install vnpy_webtrader
```


或者下载源代码后，解压后在cmd中运行：

```
pip install .
```


## 架构

* 基于Fastapi-Restful实现的主动函数调用功能，数据流程：
	1. 用户点击浏览器中的某个按钮，发起Restful功能调用；
	2. Web服务器收到Restful请求，将其转化为RPC功能调用发送给交易服务器；
	3. 交易服务器收到RPC请求，执行具体的功能逻辑，并返回结果；
	4. Web服务器返回Restful请求的结果给浏览器。

* 基于Fastapi-Websocket实现的被动数据推送功能，数据流程：
	1. 交易服务器的事件引擎转发某个事件推送，并推送给RPC客户端（Web服务器）；
	2. Web服务器收到事件推送后，将其转化为json格式，并通过Websocket发出；
	3. 浏览器通过Websocket收到推送的数据，并渲染在Web前端界面上。

* 将程序分为两个进程的主要原因包括：
	1. 交易服务器中的策略运行和数据计算的运算压力较大，需要保证尽可能保证低延时效率；
	2. Web服务器需要面对互联网访问，将交易相关的逻辑剥离能更好保证安全性。
