""""""
from PyQt5.QtWidgets import QCheckBox, QLabel, QLineEdit, QPushButton, QWidget, QGridLayout
from PyQt5 import QtGui


class Example(QWidget):
    """"""
    def __init__(self):
        """"""
        super().__init__()
        self.initUI()
        self.username = "test"
        self.password = "test"
        self.req_address = "tcp://127.0.0.1:2014"
        self.sub_address = "tcp://127.0.0.1:4102"
        self.secret_key = "dfd11067782d62fe888b73eca97bdb0e5b2ddb7e3e6e0fd9d88a302a9b2d0b1a"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = "30"

    def initUI(self):
        """"""
        # Grid布局
        grid = QGridLayout()
        self.setLayout(grid)

        # 背景颜色
        palette1 = QtGui.QPalette()
        palette1.setColor(self.backgroundRole(), QtGui.QColor(25, 35, 45))
        self.setPalette(palette1)
        self.setAutoFillBackground(True)

        # 字体大小
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)

        # 用户名标签
        username = QLabel("用户名")
        grid.addWidget(username, *(0, 0))
        username.setFont(font)
        username.setStyleSheet("color:#C8C8C8")

        # 密码标签
        password = QLabel("密码")
        grid.addWidget(password, *(1, 0))
        password.setFont(font)
        password.setStyleSheet("color:#C8C8C8")

        # REQ_ADDRESS标签
        req_address = QLabel("REQ_ADDRESS")
        grid.addWidget(req_address, *(2, 0))
        req_address.setFont(font)
        req_address.setStyleSheet("color:#C8C8C8")

        # SUB_ADDRESS标签
        sub_address = QLabel("SUB_ADDRESS")
        grid.addWidget(sub_address, *(3, 0))
        sub_address.setFont(font)
        sub_address.setStyleSheet("color:#C8C8C8")

        # SECRET_KEY标签
        secret_key = QLabel("SECRET_KEY")
        grid.addWidget(secret_key, *(4, 0))
        secret_key.setFont(font)
        secret_key.setStyleSheet("color:#C8C8C8")

        # ALGORITHM标签
        algorithm = QLabel("ALGORITHM")
        grid.addWidget(algorithm, *(5, 0))
        algorithm.setFont(font)
        algorithm.setStyleSheet("color:#C8C8C8")

        # ACCESS_TOKEN_EXPIRE_MINUTES标签
        access_token_expire_minutes = QLabel("TOKEN_MINUTES")
        grid.addWidget(access_token_expire_minutes, *(6, 0))
        access_token_expire_minutes.setFont(font)
        access_token_expire_minutes.setStyleSheet("color:#C8C8C8")

        # 保存标签
        save = QLabel("保存")
        grid.addWidget(save, *(7, 0))
        save.setFont(font)
        save.setStyleSheet("color:#C8C8C8")

        # 用户名输入框
        username_edit = QLineEdit(self)
        grid.addWidget(username_edit, *(0, 1))
        username_edit.setStyleSheet("background-color:#19232D;color:#C8C8C8;font-size:18px;font-weight:bold;font-family:Arial;")
        username_edit.textChanged[str].connect(self.on_change_username)
        # username_edit.setPlaceholderText("test")
        username_edit.setText("test")

        # 密码输入框
        password_edit = QLineEdit(self)
        grid.addWidget(password_edit, *(1, 1))
        password_edit.setStyleSheet("background-color:#19232D;color:#C8C8C8;font-size:18px;font-weight:bold;font-family:Arial;")
        password_edit.textChanged[str].connect(self.on_change_password)
        # password_edit.setPlaceholderText("test")
        password_edit.setText("test")

        # REQ_ADDRESS输入框
        req_address_edit = QLineEdit(self)
        grid.addWidget(req_address_edit, *(2, 1))
        req_address_edit.setStyleSheet("background-color:#19232D;color:#C8C8C8;font-size:18px;font-weight:bold;font-family:Arial;")
        req_address_edit.textChanged[str].connect(self.on_change_req_address)
        # req_address_edit.setPlaceholderText("tcp://127.0.0.1:2014")
        req_address_edit.setText("tcp://127.0.0.1:2014")

        # SUB_ADDRESS输入框
        sub_address_edit = QLineEdit(self)
        grid.addWidget(sub_address_edit, *(3, 1))
        sub_address_edit.setStyleSheet("background-color:#19232D;color:#C8C8C8;font-size:18px;font-weight:bold;font-family:Arial;")
        sub_address_edit.textChanged[str].connect(self.on_change_sub_address)
        # sub_address_edit.setPlaceholderText("tcp://127.0.0.1:4102")
        sub_address_edit.setText("tcp://127.0.0.1:4102")

        # SECRET_KEY输入框
        secret_key_edit = QLineEdit(self)
        grid.addWidget(secret_key_edit, *(4, 1))
        secret_key_edit.setStyleSheet("background-color:#19232D;color:#C8C8C8;font-size:18px;font-weight:bold;font-family:Arial;")
        secret_key_edit.textChanged[str].connect(self.on_change_secret_key)
        # secret_key_edit.setPlaceholderText("dfd11067782d62fe888b73eca97bdb0e5b2ddb7e3e6e0fd9d88a302a9b2d0b1a")
        secret_key_edit.setText("dfd11067782d62fe888b73eca97bdb0e5b2ddb7e3e6e0fd9d88a302a9b2d0b1a")

        # ALGORITHM输入框
        algorithm_edit = QLineEdit(self)
        grid.addWidget(algorithm_edit, *(5, 1))
        algorithm_edit.setStyleSheet("background-color:#19232D;color:#C8C8C8;font-size:18px;font-weight:bold;font-family:Arial;")
        algorithm_edit.textChanged[str].connect(self.on_change_algorithm)
        # algorithm_edit.setPlaceholderText("HS256")
        algorithm_edit.setText("HS256")

        # ACCESS_TOKEN_EXPIRE_MINUTES输入框
        access_token_expire_minutes_edit = QLineEdit(self)
        grid.addWidget(access_token_expire_minutes_edit, *(6, 1))
        access_token_expire_minutes_edit.setStyleSheet("background-color:#19232D;color:#C8C8C8;font-size:18px;font-weight:bold;font-family:Arial;")
        access_token_expire_minutes_edit.textChanged[str].connect(self.on_change_access_token_expire_minutes)
        # access_token_expire_minutes_edit.setPlaceholderText("30")
        access_token_expire_minutes_edit.setText("30")

        # 保存复选框
        is_saved = QCheckBox("", self)
        grid.addWidget(is_saved, *(7, 1))

        # 登陆按钮
        start_engine = QPushButton("启动", self)
        grid.addWidget(start_engine, *(8, 1))
        start_engine.clicked[bool].connect(self.login_trade)

        self.setGeometry(300, 300, 400, 500)
        self.setWindowTitle("启动")
        self.show()

    def on_change_username(self, text):
        self.username = text

    def on_change_password(self, text):
        self.password = text

    def on_change_req_address(self, text):
        self.req_address = text

    def on_change_sub_address(self, text):
        self.sub_address = text

    def on_change_secret_key(self, text):
        self.secret_key = text

    def on_change_algorithm(self, text):
        self.algorithm = text

    def on_change_access_token_expire_minutes(self, text):
        self.access_token_expire_minutes = text

    def login_trade(self):
        # subprocess.run(["python", "c:/Users/guoyifan/Documents/vnpy_webtrader/script/run.py"])
        print(self.username, self.password, self.req_address, self.sub_address, self.secret_key, self.algorithm, self.access_token_expire_minutes)
