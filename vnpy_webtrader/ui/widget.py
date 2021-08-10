""""""
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets
from vnpy_webtrader.engine import APP_NAME


class WebTrade(QtWidgets.QDialog):
    """"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        self.wt_engine = main_engine.get_engine(APP_NAME)

        self.init_ui()

    def init_ui(self):
        """"""
        self.setWindowTitle("网页端服务")

        # Create widgets
        self.active_combo = QtWidgets.QComboBox()
        self.active_combo.addItems(["停止", "启动"])

        self.username = WebTradeLineEdit("test")
        self.password = WebTradeLineEdit("test")
        self.req_address = WebTradeLineEdit("tcp://127.0.0.1:2014")
        self.sub_address = WebTradeLineEdit("tcp://127.0.0.1:4102")
        self.secret_key = WebTradeLineEdit("dfd11067782d62fe888b73eca97bdb0e5b2ddb7e3e6e0fd9d88a302a9b2d0b1a")
        self.algorithm = WebTradeLineEdit("HS256")
        self.access_token_expire_minutes = WebTradeLineEdit("30")

        start_button = QtWidgets.QPushButton("启动")
        start_button.clicked.connect(self.start_webserve)

        # Form layout
        form = QtWidgets.QFormLayout()
        form.addRow("运行状态", self.active_combo)
        form.addRow("用户名", self.username)
        form.addRow("密码", self.password)
        form.addRow("REQ_ADDRESS", self.req_address)
        form.addRow("SUB_ADDRESS", self.sub_address)
        form.addRow("SECRET_KEY", self.secret_key)
        form.addRow("ALGORITHM", self.algorithm)
        form.addRow("TOKEN_MINUTES", self.access_token_expire_minutes)
        form.addRow(start_button)

        self.setLayout(form)

        # Set Fix Size
        hint = self.sizeHint()
        self.setFixedSize(hint.width() * 1.2, hint.height())
        self.show()

    def start_webserve(self):
        """"""
        active_text = self.active_combo.currentText()
        if active_text == "启动":
            active = True
            self.active_combo.setCurrentIndex(0)
        else:
            active = False
            self.active_combo.setCurrentIndex(1)

        setting = {
            "active": active,
            "username": self.username.text(),
            "password": self.password.text(),
            "req_address": self.req_address.text(),
            "sub_address": self.sub_address.text(),
            "secret_key": self.secret_key.text(),
            "algorithm": self.algorithm.text(),
            "access_token_expire_minutes": self.access_token_expire_minutes.text(),
        }

        self.wt_engine.start_trade(setting)

    def exec_(self):
        """"""
        super().exec_()


class WebTradeLineEdit(QtWidgets.QLineEdit):
    """"""
    def __init__(self, value: str = "a"):
        """"""
        super().__init__()
        self.setText(value)
