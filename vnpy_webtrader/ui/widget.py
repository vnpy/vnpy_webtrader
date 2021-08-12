from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets

from ..engine import APP_NAME, WebEngine


class WebManager(QtWidgets.QDialog):
    """网页服务器管理界面"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine
        self.web_engine: WebEngine = main_engine.get_engine(APP_NAME)

        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Web服务器")

        self.username = QtWidgets.QLineEdit("test")
        self.password = QtWidgets.QLineEdit("test")
        self.req_address = QtWidgets.QLineEdit("tcp://127.0.0.1:2014")
        self.sub_address = QtWidgets.QLineEdit("tcp://127.0.0.1:4102")
        self.secret_key = QtWidgets.QLineEdit("dfd11067782d62fe888b73eca97bdb0e5b2ddb7e3e6e0fd9d88a302a9b2d0b1a")

        self.start_button = QtWidgets.QPushButton("启动")
        self.start_button.clicked.connect(self.start)

        # Form layout
        form = QtWidgets.QFormLayout()
        form.addRow("用户名", self.username)
        form.addRow("密码", self.password)
        form.addRow("请求地址", self.req_address)
        form.addRow("请阅地址", self.sub_address)
        form.addRow("密钥", self.secret_key)
        form.addRow(self.start_button)

        self.setLayout(form)

        # Set Fix Size
        hint = self.sizeHint()
        self.setFixedSize(hint.width() * 1.2, hint.height())
        self.show()

    def start(self):
        """启动引擎"""
        self.web_engine.start_server(
            self.req_address.text(),
            self.sub_address.text(),
        )
        self.start_button.setDisabled(True)
