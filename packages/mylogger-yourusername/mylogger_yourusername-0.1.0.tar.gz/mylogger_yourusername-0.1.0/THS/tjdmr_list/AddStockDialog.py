import sys
import re
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import QMessageBox
from santou.DeaiClientData import DeaiClientData


def get_button_style():
    """Returns the style for the buttons."""
    return """
        QPushButton {
            background-color: #fd7e14;  /* 按钮背景色 */
            color: white;              /* 按钮文字颜色 */
            font-size: 15px;           /* 按钮字体大小 */
            border: none;              /* 去掉边框 */
            border-radius: 5px;        /* 圆角边框 */
        }

        QPushButton:pressed {
            background-color: #FFCCCB; /* 按下时的背景色 */
        }
    """


class AddStockDialog(QDialog):
    def __init__(self, parent=None):
        super(AddStockDialog, self).__init__(parent)
        self.setWindowTitle("添加股票")
        self.setFixedSize(320, 300)  # 调整窗口大小
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        # 主布局
        main_layout = QHBoxLayout()

        # 左侧布局：放置 QListWidget
        left_layout = QVBoxLayout()
        self.stock_list = QListWidget()
        self.stock_list.setFixedWidth(150)  # 设置固定宽度
        left_layout.addWidget(self.stock_list)
        main_layout.addLayout(left_layout)

        # 右侧布局
        right_layout = QVBoxLayout()
        right_layout.setSpacing(0)
        # 输入框
        self.input_box = QLineEdit()
        self.input_box.setFixedHeight(25)
        self.input_box.setPlaceholderText("请输入 股票名称/代码")
        self.input_box.textChanged.connect(self.handle_input_changed)
        right_layout.addWidget(self.input_box)

        # 隐藏的下拉框
        self.hidden_list = QListWidget()
        self.hidden_list.setFixedWidth(150)
        self.hidden_list.setFixedHeight(150)
        self.hidden_list.setVisible(False)
        self.hidden_list.itemClicked.connect(self.handle_hidden_item_clicked)

        # 设置隐藏列表的字体大小
        font = self.hidden_list.font()
        font.setPointSize(10)  # 可根据需要调整字体大小
        self.hidden_list.setFont(font)

        right_layout.addWidget(self.hidden_list)

        # 添加一个伸缩空间，将按钮推到最下面
        right_layout.addStretch()
        # 确定按钮
        self.confirm_button = QPushButton("确定")
        self.confirm_button.setStyleSheet(get_button_style())
        self.confirm_button.setFixedSize(100, 30)
        self.confirm_button.clicked.connect(self.handle_confirm)
        right_layout.addWidget(self.confirm_button, alignment=Qt.AlignCenter)  # 右对齐

        # 添加一个垂直的 QSpacerItem 来设置间距为 30 像素
        spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        right_layout.addItem(spacer)
        # 删除按钮
        self.delete_button = QPushButton("删除")
        self.delete_button.setContentsMargins(0, 0, 0, 0)
        self.delete_button.setStyleSheet(get_button_style())
        self.delete_button.setFixedSize(100, 30)
        self.delete_button.clicked.connect(self.handle_delete_stock)
        right_layout.addWidget(self.delete_button, alignment=Qt.AlignCenter)  # 右对齐
        # 添加一个垂直的 QSpacerItem 来设置间距为 100 像素
       # spacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Fixed)
       # right_layout.addItem(spacer)

        # 将右侧布局添加到主布局
        main_layout.addLayout(right_layout)

        # 设置主布局
        self.setLayout(main_layout)

    def handle_input_changed(self):
        """输入框内容变化时的处理"""
        input_text = self.input_box.text().strip()

        # 使用正则表达式限制只能输入汉字或数字
        if not re.match("^[\u4e00-\u9fa5\d]*$", input_text):
            self.input_box.setText(re.sub("[^\u4e00-\u9fa5\d]", "", input_text))
            return

        if input_text:
            # 查询数据库
            action = "check_stock"
            params = input_text

            # 查询数据库
            deal = DeaiClientData()
            result = deal.check_stock(action, params)  # 假设数据库有一个方法可以检查股票是否存在
            self.hidden_list.clear()
            if result:
                for stock in result:
                    self.hidden_list.addItem(f"{stock['gpdm']}-{stock['gpmc']}")
                self.hidden_list.setVisible(True)
            else:
                self.hidden_list.setVisible(False)
        else:
            self.hidden_list.setVisible(False)

    def handle_hidden_item_clicked(self, item):
        """隐藏框中的项被点击时的处理"""
        stock_info = item.text()  # 获取点击的项的内容
        stock_code = stock_info.split("-")[0]  # 提取股票代码

        # 检查是否已经存在于左边的列表中
        is_duplicate = False
        for index in range(self.stock_list.count()):
            existing_item = self.stock_list.item(index).text()
            existing_code = existing_item.split("-")[0]
            if existing_code == stock_code:
                is_duplicate = True
                break

        if is_duplicate:
            # 如果重复，弹出提示框
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("提示")
            msg_box.setText("该股票已存在，不能重复添加！")

            # 设置按钮为 "是"，并调整按钮大小
            yes_button = msg_box.addButton("是", QMessageBox.YesRole)
            yes_button.setFixedSize(50, 30)

            msg_box.exec()
        else:
            # 如果不重复，添加到左边的列表中
            self.stock_list.addItem(stock_info)
            self.input_box.clear()
            self.hidden_list.setVisible(False)

    def handle_delete_stock(self):
        """删除选中的股票"""
        selected_item = self.stock_list.currentItem()
        if selected_item:
            # 自定义警告框：确认删除
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("警告")
            msg_box.setText("确定要删除选中的股票吗？")

            # 设置按钮为 "是"，并调整按钮大小
            yes_button = msg_box.addButton("是", QMessageBox.YesRole)
            yes_button.setFixedSize(50, 30)

            # 添加 "取消" 按钮
            cancel_button = msg_box.addButton("取消", QMessageBox.NoRole)
            cancel_button.setFixedSize(50, 30)

            # 显示对话框并等待用户选择
            msg_box.exec()

            # 如果用户点击了 "是"，则删除选中的股票
            if msg_box.clickedButton() == yes_button:
                self.stock_list.takeItem(self.stock_list.row(selected_item))
        else:
            # 自定义警告框：未选择股票
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("警告")
            msg_box.setText("请先选择一个股票！")

            # 设置按钮为 "是"，并调整按钮大小
            yes_button = msg_box.addButton("是", QMessageBox.YesRole)
            yes_button.setFixedSize(50, 30)

            msg_box.exec()

    def handle_confirm(self):
        """确定按钮点击事件"""
        input_text = self.input_box.text().strip()


        selected_stocks = []
        for index in range(self.stock_list.count()):
            selected_stocks.append(self.stock_list.item(index).text().split("-")[0])

        if selected_stocks:
            # 发送信号，传递选中的股票代码
            self.parent().update_table_with_stocks(selected_stocks)
            self.stock_list.clear()
            #self.close()
        else:
            # 自定义警告框：未选择股票
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("警告")
            msg_box.setText("未选择任何股票！")

            # 设置按钮为 "是"，并调整按钮大小
            yes_button = msg_box.addButton("是", QMessageBox.YesRole)
            yes_button.setFixedSize(50, 30)
            msg_box.exec()


