import sys

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets, QtCore
from vnpy.trader.utility import load_json, save_json, get_file_path

from ..engine import APP_NAME, WebEngine


class WebManager(QtWidgets.QWidget):
    """网页服务器管理界面"""

    setting_filename = "web_trader_setting.json"
    setting_filepath = get_file_path(setting_filename)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine
        self.web_engine: WebEngine = main_engine.get_engine(APP_NAME)

        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Web服务")

        setting = load_json(self.setting_filepath)
        username = setting.get("username", "vnpy")
        password = setting.get("password", "vnpy")
        req_address = setting.get("req_address", "tcp://127.0.0.1:2014")
        sub_address = setting.get("sub_address", "tcp://127.0.0.1:4102")
        host = setting.get("host", "127.0.0.1")
        port = setting.get("port", "8000")

        self.username_line = QtWidgets.QLineEdit(username)
        self.password_line = QtWidgets.QLineEdit(password)
        self.req_line = QtWidgets.QLineEdit(req_address)
        self.sub_line = QtWidgets.QLineEdit(sub_address)
        self.host_line = QtWidgets.QLineEdit(host)
        self.port_line = QtWidgets.QLineEdit(port)

        self.start_button = QtWidgets.QPushButton("启动")
        self.start_button.clicked.connect(self.start)

        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)

        form = QtWidgets.QFormLayout()
        form.addRow("用户名", self.username_line)
        form.addRow("密码", self.password_line)
        form.addRow("请求地址", self.req_line)
        form.addRow("请阅地址", self.sub_line)
        form.addRow("监听地址", self.host_line)
        form.addRow("监听端口", self.port_line)
        form.addRow(self.start_button)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(form)
        hbox.addWidget(self.text_edit)
        self.setLayout(hbox)

        self.resize(1000, 500)

    def start(self):
        """启动引擎"""
        username: str = self.username_line.text()
        password: str = self.password_line.text()
        req_address: str = self.req_line.text()
        sub_address: str = self.sub_line.text()
        host: str = self.host_line.text()
        port: str = self.port_line.text()

        # 保存配置
        setting = {
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
        self.process = QtCore.QProcess(self)
        self.process.setProcessChannelMode(self.process.MergedChannels)

        self.process.readyReadStandardOutput.connect(self.data_ready)
        self.process.readyReadStandardError.connect(self.data_ready)
        self.process.started.connect(self.web_started)
        self.process.finished.connect(self.web_finished)

        # 启动子进程
        cmd = [
            "-m"
            "uvicorn",
            "vnpy_webtrader.web:app",
            f"--host={host}",
            f"--port={port}",
            "--reload"
        ]
        self.process.start(sys.executable, cmd)

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

    def web_finished(self) -> None:
        """Web进程结束"""
        self.text_edit.append("Web服务器停止")

    def data_ready(self) -> None:
        """更新进程有数据可读"""
        text = bytes(self.process.readAll())

        try:
            text = text.decode("UTF8")
        except UnicodeDecodeError:
            text = text.decode("GBK")

        self.text_edit.append(text)
