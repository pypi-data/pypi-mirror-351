from PySide6.QtWidgets import *

from PySide6.QtWidgets import QMessageBox
from DeaiClientData import DeaiClientData
from PySide6.QtCore import Signal
import pyautogui

#新增打板窗口,和其他窗口独立开
class CreateSbZtWindow(QWidget):
    signal = Signal()
    def __init__(self):
        super(CreateSbZtWindow, self).__init__()
        screen_width, screen_height = pyautogui.size()
        self.setWindowTitle("打板主题")
        self.setFixedSize(1050, 710)
        # 定义信号，用于通知主窗口刷新表格

        # 创建大的垂直布局
        layout = QVBoxLayout()

        # 输入框1 - 主题名称
        self.input1_label = QLabel("主题名称：")
        self.input1 = QLineEdit()
        self.input1.setPlaceholderText("请输入主题名称（必填）")
        layout.addWidget(self.input1_label)
        layout.addWidget(self.input1)

        # 输入框2 - 描述信息（多行）
        self.input2_label = QLabel("描述信息：")
        self.input2 = QTextEdit()  # 多行输入框
        self.input2.setPlaceholderText("请输入详细的描述信息（可选）")
        layout.addWidget(self.input2_label)
        layout.addWidget(self.input2)

        # 添加提交按钮
        self.submit_button = QPushButton("提交")
        self.submit_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        self.submit_button.clicked.connect(self.submit_form)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submit_form(self):
        # 获取输入框内容 json.dumps(data)
        topic_name = self.input1.text().strip()  # 去掉两端空格
        description = self.input2.toPlainText().strip() # 获取 QTextEdit 的内容
        action="deal_sbmx_data"
        # 校验主题名称是否为空
        if not topic_name:
            QMessageBox.warning(self, "警告", "主题名称为必填项，请填写！")
            return
        deal = DeaiClientData()
        respon=deal.Composite_sbmx_Data(action,topic_name, description)
        print(f"sbtable:{respon}")
        # 提交成功的提示
        if respon["message"]=="success":
            QMessageBox.information(self, "成功", f"主题已创建：\n主题名称：{topic_name}\n描述信息：{description or '无'}")

            # 发射信号通知刷新表格
            self.signal.emit()
        else:
            QMessageBox.information(self, "失败", f"{respon}")
        self.close()  # 关闭窗口

