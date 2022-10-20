import sys
from pathlib import Path

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets, QtCore
from vnpy.trader.utility import load_json, save_json, get_file_path

from ..engine import APP_NAME, WebEngine


class WebManager(QtWidgets.QWidget):
    """网页服务器管理界面"""

    setting_filename: str = "web_trader_setting.json"
    setting_filepath: Path = get_file_path(setting_filename)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine
        self.web_engine: WebEngine = main_engine.get_engine(APP_NAME)

        self.init_ui()

    def init_ui(self) -> None:
        """初始化界面"""
        self.setWindowTitle("Web服务")

        setting: dict = load_json(self.setting_filepath)
        username: str = setting.get("username", "vnpy")
        password: str = setting.get("password", "vnpy")
        req_address: str = setting.get("req_address", "tcp://127.0.0.1:2014")
        sub_address: str = setting.get("sub_address", "tcp://127.0.0.1:4102")
        host: str = setting.get("host", "127.0.0.1")
        port: str = setting.get("port", "8000")

        self.username_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit(username)
        self.password_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit(password)
        self.req_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit(req_address)
        self.sub_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit(sub_address)
        self.host_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit(host)
        self.port_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit(port)

        self.start_button: QtWidgets.QPushButton = QtWidgets.QPushButton("启动")
        self.start_button.clicked.connect(self.start)

        self.end_button: QtWidgets.QPushButton = QtWidgets.QPushButton("停止")
        self.end_button.clicked.connect(self.end)

        self.text_edit: QtWidgets.QTextEdit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)

        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()
        form.addRow("用户名", self.username_line)
        form.addRow("密码", self.password_line)
        form.addRow("请求地址", self.req_line)
        form.addRow("订阅地址", self.sub_line)
        form.addRow("监听地址", self.host_line)
        form.addRow("监听端口", self.port_line)
        form.addRow(self.start_button)
        form.addRow(self.end_button)

        self.end_button.setEnabled(False)

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addLayout(form)
        hbox.addWidget(self.text_edit)
        self.setLayout(hbox)

        self.resize(1000, 500)

    def start(self) -> None:
        """启动引擎"""
        username: str = self.username_line.text()
        password: str = self.password_line.text()
        req_address: str = self.req_line.text()
        sub_address: str = self.sub_line.text()
        host: str = self.host_line.text()
        port: str = self.port_line.text()

        # 保存配置
        setting: dict = {
            "username": username,
            "password": password,
            "req_address": req_address,
            "sub_address": sub_address,
            "host": host,
            "port": port
        }
        save_json(self.setting_filepath, setting)

        # 启动RPC
        self.web_engine.start_server(req_address, sub_address)
        self.start_button.setDisabled(True)

        # 初始化Web服务子进程
        self.process: QtCore.QProcess = QtCore.QProcess(self)
        self.process.setProcessChannelMode(self.process.MergedChannels)

        self.process.readyReadStandardOutput.connect(self.data_ready)
        self.process.readyReadStandardError.connect(self.data_ready)
        self.process.started.connect(self.web_started)
        self.process.finished.connect(self.web_finished)

        # 启动子进程
        cmd: list = [
            "-m"
            "uvicorn",
            "vnpy_webtrader.web:app",
            f"--host={host}",
            f"--port={port}"
        ]
        self.process.start(sys.executable, cmd)

    def end(self) -> None:
        """终止引擎"""
        self.process.kill()

    def web_started(self) -> None:
        """Web进程启动"""
        self.text_edit.append("Web服务器启动")

        for w in [
            self.username_line,
            self.password_line,
            self.req_line,
            self.sub_line,
            self.host_line,
            self.port_line,
            self.start_button
        ]:
            w.setEnabled(False)

        self.end_button.setEnabled(True)

    def web_finished(self) -> None:
        """Web进程结束"""
        self.text_edit.append("Web服务器停止")

        for w in [
            self.username_line,
            self.password_line,
            self.req_line,
            self.sub_line,
            self.host_line,
            self.port_line,
            self.start_button
        ]:
            w.setEnabled(True)

        self.end_button.setEnabled(False)

    def data_ready(self) -> None:
        """更新进程有数据可读"""
        text: bytes = bytes(self.process.readAll())

        try:
            text: str = text.decode("UTF8")
        except UnicodeDecodeError:
            text: str = text.decode("GBK")

        self.text_edit.append(text)
