from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets
from ..engine import APP_NAME


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

        self.username = RiskManagerSpinBox()
        self.password = RiskManagerSpinBox()
        self.req_address = RiskManagerSpinBox()
        self.sub_address = RiskManagerSpinBox()
        self.secret_key = RiskManagerSpinBox()
        self.algorithm = RiskManagerSpinBox()
        self.access_token_expire_minutes = RiskManagerSpinBox()

        save_button = QtWidgets.QPushButton("保存")
        save_button.clicked.connect(self.save_setting)

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
        form.addRow(save_button)

        self.setLayout(form)

        # Set Fix Size
        hint = self.sizeHint()
        self.setFixedSize(hint.width() * 1.2, hint.height())

    def save_setting(self):
        """"""
        active_text = self.active_combo.currentText()
        if active_text == "启动":
            active = True
        else:
            active = False

        setting = {
            "active": active,
            "username": self.username.value(),
            "password": self.password.value(),
            "req_address": self.req_address.value(),
            "sub_address": self.sub_address.value(),
            "secret_key": self.secret_key.value(),
            "algorithm": self.algorithm.value(),
            "access_token_expire_minutes": self.access_token_expire_minutes.value(),
        }

        self.wt_engine.update_setting(setting)
        self.wt_engine.save_setting()

        self.close()

    def update_setting(self):
        """"""
        setting = self.wt_engine.get_setting()
        if setting["active"]:
            self.active_combo.setCurrentIndex(1)
        else:
            self.active_combo.setCurrentIndex(0)

        self.username.setValue(setting["username"])
        self.password.setValue(setting["password"])
        self.req_address.setValue(setting["req_address"])
        self.sub_address.setValue(setting["sub_address"])
        self.secret_key.setValue(setting["secret_key"])
        self.algorithm.setValue(setting["algorithm"])
        self.access_token_expire_minutes.setValue(setting["access_token_expire_minutes"])

    def exec_(self):
        """"""
        self.update_setting()
        super().exec_()


class RiskManagerSpinBox(QtWidgets.QSpinBox):
    """"""

    def __init__(self, value: int = 0):
        """"""
        super().__init__()
        self.setMinimum(0)
        self.setMaximum(1000000)
        self.setValue(value)
