from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QObject, Signal, QThread
import sys
from santou.DeaiClientData import DeaiClientData
from santou.mi import md5_jiami
from datetime import datetime


class AccountSignal(QObject):
    timeout = Signal()


class AccountWorker(QThread):
    finished = Signal(object)

    def __init__(self, action, acc):
        super().__init__()
        self.action = action
        self.acc = acc
        self.deal = DeaiClientData()

    def run(self):
        try:
            data = self.deal.yz_account(self.action, self.acc)
            self.finished.emit(data)
        except Exception as e:
            self.finished.emit(None)


class Account:
    _instance = None
    username = None
    zh_lx = None
    time = None
    qq = None
    wechat = None
    acc = None
    start_rq = ''
    end_rq = ''
    _app_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if not QApplication.instance():
                QApplication(sys.argv)
                cls._app_initialized = True
            cls.signal = AccountSignal()
            cls.signal.timeout.connect(cls._show_timeout_dialog)
        return cls._instance

    def __init__(self):
        self.init_account()

    def init_account(self):
        if self.zh_lx is None:
            acc = md5_jiami().get_md5()
            action = "yz_account"

            # 启动工作线程
            self.worker = AccountWorker(action, acc)
            self.worker.finished.connect(self._handle_response)
            self.worker.start()

            # 启动超时检测
            QThread.currentThread().msleep(10000)  # 等待10秒
            if not self.worker.isFinished():
                self.signal.timeout.emit()
                self.worker.terminate()

    def _handle_response(self, data):
        if data:
            Account.qq = data["qq"]
            Account.wechat = data["wechat"]
            Account.username = data["id"]
            Account.acc = data["acc"]
            if data["zh_lx"]:
                Account.start_rq = data["start_rq"]
                Account.end_rq = data["end_rq"]

                today = datetime.now().date()
                start_date = datetime.strptime(Account.start_rq, '%Y-%m-%d').date()
                end_date = datetime.strptime(Account.end_rq, '%Y-%m-%d').date()

                if start_date <= today <= end_date:
                    Account.zh_lx = data["zh_lx"]
                else:
                    print(f"账户已经过了有效期，请联系管理员！")
            else:
                print(f"账户未开通，请联系管理员开户！")

    @classmethod
    def _show_timeout_dialog(cls):
        msg = QMessageBox()
        msg.setWindowTitle("连接超时")
        msg.setIcon(QMessageBox.Critical)
        msg.setText("服务器访问超时，请联系我们: qq:366310986 微信：trader_win_123")

        # 添加中文按钮
        retry_btn = msg.addButton("重试", QMessageBox.ActionRole)
        close_btn = msg.addButton("关闭", QMessageBox.RejectRole)

        msg.exec_()

        if msg.clickedButton() == retry_btn:
            cls._instance.init_account()

    # 保持原有方法不变
    def get_time(self):
        if Account.zh_lx == "0.9s":
            return 900
        if Account.zh_lx == "0.6s":
            return 600
        elif Account.zh_lx == "3s":
            return 3000
        elif Account.zh_lx == "0.3s":
            return 300
        else:
            return 300000000

    @classmethod
    def get_username(cls):
        return Account.username

    @classmethod
    def get_zh_lx_time(cls):
        return cls.time


if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    account = Account()
    if Account._app_initialized:
        sys.exit(app.exec())