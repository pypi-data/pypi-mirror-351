from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout,
                               QLineEdit, QLabel, QPushButton, QMessageBox, QDialog, QHBoxLayout)
from PySide6.QtCore import Qt, QTimer
import sys
from santou.main import Window
from santou.account import Account
from santou.DeaiClientData import DeaiClientData
from santou.mi import md5_jiami
import os


def get_base_path():
    if hasattr(sys, "frozen") and sys.frozen:
        # 打包后的路径（Nuitka 建议使用 sys.executable 的目录）
        base_dir = os.path.dirname(sys.executable)
        return base_dir
    else:
        # 开发环境的路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return base_dir


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()

        QTimer.singleShot(0, self.check_and_show)
        self.deal = DeaiClientData()
        self.acc = md5_jiami().get_md5()
        print(self.acc)
    def check_and_show(self):
        if Account.zh_lx:
            self.close()
            self.main_window = Window()
            self.main_window.show()
        else:
            self.base_dir = get_base_path()  # 获取基础路径
            photo_path = os.path.join(self.base_dir,'photo', 'title_top.png')

            self.setWindowIcon(QIcon(photo_path))
            self.setWindowTitle("量化赢家1.0")
            self.setup_ui()
            self.setMinimumSize(500, 250)

    def closeEvent(self, event):
        # 检查这里是否有阻止窗口关闭的逻辑
        # 例如 event.ignore() 会阻止窗口关闭
        event.accept()  # 确保事件被接受，允许窗口关闭

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 标题
        title_label = QLabel("账号注册")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #34495e;
            margin-bottom: 20px;
        """)
        main_layout.addWidget(title_label)

        # 表单布局
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)  # 行间距
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # QQ账号输入框
        self.qq_input = QLineEdit()
        self.qq_input.setPlaceholderText("请输入您和我们联系时用到的QQ号码")
        self.qq_input.setMinimumHeight(35)
        self.qq_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        # self.qq_input.textChanged.connect(self.check_duplicate)

        # 微信账号输入框
        self.wechat_input = QLineEdit()
        self.wechat_input.setPlaceholderText("请输入您和我们联系时用到的微信ID")
        self.wechat_input.setMinimumHeight(35)
        self.wechat_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #2ecc71;
            }
        """)
        # self.wechat_input.textChanged.connect(self.check_duplicate)

        # 添加表单行
        form_layout.addRow("QQ号码：", self.qq_input)
        form_layout.addRow("微信ID：", self.wechat_input)

        # 提示信息
        hint_label = QLabel("注意：\n• 至少需要填写一个有效账号，该账号是用于你和我们常联系的账号，请不要随意填写。\n• 权限申请、找回等操作将根据您填写的账号进行验证")
        hint_label.setStyleSheet("""
            color: red;
            font-size: 12px;
            padding: 10px;
            background: #fdebd0;
            border-radius: 5px;
            border: 1px solid #f1c40f;
            margin-top: 15px;
        """)
        hint_label.setWordWrap(True)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(hint_label)

        # 创建一个水平布局，用于放置“联系我们”按钮和“提交注册”按钮
        button_layout = QHBoxLayout()

        # 添加“联系我们”按钮到水平布局的最左边
        self.contact_btn = QPushButton("联系我们")
        self.contact_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 16px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:pressed {
                background: #1c5980;
            }
        """)
        self.contact_btn.clicked.connect(self.show_connect_info)
        button_layout.addWidget(self.contact_btn)

        # 添加一个弹簧，将“提交注册”按钮推到右侧
        button_layout.addStretch()

        # 添加“提交注册”按钮到水平布局的右侧
        self.submit_btn = QPushButton("提交注册")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 16px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: #219a52;
            }
            QPushButton:pressed {
                background: #1d8348;
            }
        """)
        self.submit_btn.clicked.connect(self.on_submit)
        button_layout.addWidget(self.submit_btn)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

    def check_duplicate(self, qq, wechat):
        if str:
            action = "check_duplicate_zh"
            result = self.deal.check_duplicate_zh(action, self.acc, qq, wechat)

        self.submit_btn.setEnabled(True)

    def on_submit(self):
        qq = self.qq_input.text().strip()
        wechat = self.wechat_input.text().strip()

        if not qq and not wechat:
            QMessageBox.warning(
                self,
                "输入错误",
                "至少需要填写QQ账号和微信ID其中一个注册账号！",
                QMessageBox.StandardButton.Ok
            )
            return
        result = self.check_duplicate(qq, wechat)

        if result:
            if result["qq"] == qq:
                QMessageBox.warning(
                    self,
                    "账号重复",
                    "qq号码已存在，请联系管理员！",
                    QMessageBox.StandardButton.Ok
                )
                return
            if result["wechat"] == wechat:
                QMessageBox.warning(
                    self,
                    "账号重复",
                    "微信ID已存在，请联系管理员！",
                    QMessageBox.StandardButton.Ok
                )
                if result["acc"] == self.acc:
                    QMessageBox.warning(
                        self,
                        "账号重复",
                        "你已经注册过，请联系管理员！",
                        QMessageBox.StandardButton.Ok
                    )
                return
        else:
            acc = md5_jiami().get_md5()
            action = "save_register_zh"
            result = self.deal.save_register_zh(action, acc, qq, wechat)
            if result["message"] == "success":
                success_msg = "账号注册成功：\n"
                if qq:
                    success_msg += f"QQ号码：{qq}\n"
                if wechat:
                    success_msg += f"微信ID：{wechat}\n"
                QMessageBox.information(
                    self,
                    "注册成功",
                    success_msg,
                    QMessageBox.StandardButton.Ok
                )

                # 关闭注册窗口并打开主界面
                self.close()
                self.main_window = Window()
                self.main_window.show()

    def show_connect_info(self):
        """显示联系信息对话框"""
        dialog = ConnectInfoDialog(self.base_dir)
        dialog.exec()


class ConnectInfoDialog(QDialog):
    def __init__(self, base_dir):
        super().__init__()
        self.setWindowTitle("联系我们")
        self.base_dir = get_base_path()
        self.setWindowIcon(QIcon(os.path.join(self.base_dir, 'title_top.png')))
        self.setFixedSize(700, 400)

        main_layout = QHBoxLayout()

        # 左边部分：QQ信息
        left_layout = QVBoxLayout()
        qq_label = QLabel("QQ账号：366310986")
        # 设置QQ账号标签的样式表，字体变大加粗
        qq_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        left_layout.addWidget(qq_label)

        qq_qr_path = os.path.join(base_dir, 'photo', 'QQ.png')
        if os.path.exists(qq_qr_path):
            qq_qr_pixmap = QPixmap(qq_qr_path)
            qq_qr_label = QLabel()
            qq_qr_label.setPixmap(qq_qr_pixmap.scaled(300, 300, Qt.KeepAspectRatio))
            left_layout.addWidget(qq_qr_label)

        # 右边部分：微信信息
        right_layout = QVBoxLayout()
        wechat_label = QLabel("微信ID：trader_win_123")
        # 设置微信ID标签的样式表，字体变大加粗
        wechat_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        right_layout.addWidget(wechat_label)

        wechat_qr_path = os.path.join(base_dir, 'photo', 'wechat.png')
        if os.path.exists(wechat_qr_path):
            wechat_qr_pixmap = QPixmap(wechat_qr_path)
            wechat_qr_label = QLabel()
            wechat_qr_label.setPixmap(wechat_qr_pixmap.scaled(300, 300, Qt.KeepAspectRatio))
            right_layout.addWidget(wechat_qr_label)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    _ = Account()  # 强制初始化

    window = RegisterWindow()
    image_path = os.path.join(get_base_path(), 'photo', 'cc.jpeg')

    window.setWindowIcon(QIcon(image_path))
    if Account.zh_lx is None:
        window.show()
    sys.exit(app.exec())