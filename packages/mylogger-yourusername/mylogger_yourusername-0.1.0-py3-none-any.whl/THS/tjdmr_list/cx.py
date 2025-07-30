import sys

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCore import Signal
from santou.DeaiClientData import DeaiClientData
import os
from santou.path import path

class Ck(QWidget):
    # 定义一个信号，用于传递选中的股票代码
    stock_codes_selected = Signal(list)

    def __init__(self,ck_table):
        super(Ck, self).__init__()
        self.ck_table = ck_table
        # 设置窗口标题和大小
        # 获取基础路径
        base_path = path().get_base_path()
        # 使用os.path.join构建日志目录路径
        log_dir = os.path.join(base_path, 'photo')
        # 构建完整日志文件路径
        log_file = os.path.join(log_dir, 'title_top.png')
        self.setWindowIcon(QIcon(log_file))

        self.setWindowTitle("查询页面")
        self.setFixedSize(599, 500)

        # 创建大的垂直布局
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # widget1 存放输入框
        self.widget1 = QWidget()
        self.widget1.setContentsMargins(0, 0, 0, 0)
        self.widget1.setFixedHeight(50)

        # 创建水平布局
        self.cx_layout = QHBoxLayout()
        self.cx_layout.setAlignment(Qt.AlignCenter)  # 使内容居中

        # 添加输入框
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("请输入概念名称，选择下方的概念板块")  # 设置输入框提示文本
        self.input_box.setFixedSize(300, 30)  # 设置输入框宽度
        self.cx_layout.addWidget(self.input_box)

        # 将水平布局添加到 widget1
        self.widget1.setLayout(self.cx_layout)

        # 创建浮动窗口
        self.floating_window = QWidget()
        self.floating_window.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)  # 去掉标题栏和边框
        self.floating_window.setFixedSize(300, 300)  # 设置浮动窗口的大小

        # 在浮动窗口中添加 QListWidget
        self.hidden_list = QListWidget()
        self.hidden_list.setStyleSheet("QListWidget { border: none; }")  # 去掉边框
        self.hidden_layout = QVBoxLayout(self.floating_window)
        self.hidden_layout.addWidget(self.hidden_list)
        self.hidden_list.itemClicked.connect(self.on_list_item_clicked)  # 绑定点击事件

        # 添加 QListWidget 和按钮的布局
        self.list_and_button_widget = QWidget()
        self.list_and_button_layout = QHBoxLayout()
        self.list_and_button_widget.setLayout(self.list_and_button_layout)

        # 添加 QListWidget
        self.result_list = QListWidget()
        self.result_list.setFixedHeight(600)  # 设置列表高度
        self.result_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)  # 允许多选
        self.list_and_button_layout.addWidget(self.result_list)

        # 添加按钮的垂直布局
        self.button_layout = QVBoxLayout()
        self.button_layout.setAlignment(Qt.AlignTop)  # 按钮靠上对齐

        # 添加确定按钮
        self.confirm_button = QPushButton("确定")
        self.confirm_button.setFixedSize(100, 30)  # 设置按钮大小
        self.confirm_button.clicked.connect(self.on_confirm_button_clicked)  # 绑定点击事件
        self.button_layout.addWidget(self.confirm_button)
        # 添加一个垂直的 QSpacerItem 来设置间距为 30 像素
        spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.button_layout.addItem(spacer)
        # 添加删除按钮
        self.delete_button = QPushButton("删除")
        self.delete_button.setFixedSize(100, 30)  # 设置按钮大小
        self.delete_button.clicked.connect(self.delete_selected_items)  # 绑定点击事件
        self.button_layout.addWidget(self.delete_button)

        # 将按钮布局添加到主布局
        self.list_and_button_layout.addLayout(self.button_layout)

        # widget2 存放股票池数据
        self.gpc_widget2 = QWidget()
        self.layout_win = QVBoxLayout(self)  # 使用垂直布局
        self.gpc_widget2.setLayout(self.layout_win)

        # 添加布局到窗口
        self.layout.addWidget(self.widget1)
        self.layout.addWidget(self.list_and_button_widget)  # 添加列表和按钮
        self.layout.addWidget(self.gpc_widget2)
        self.setLayout(self.layout)

        # 绑定输入框文本变化事件
        self.input_box.textChanged.connect(self.on_input_text_changed)

    def on_input_text_changed(self):
        """输入框文本变化事件处理函数"""
        query_text = self.input_box.text().strip()  # 获取输入框内容

        if query_text:  # 如果输入框不为空
            # 触发数据库查询
            params = query_text
            action = 'like_query_ck'
            deal = DeaiClientData()
            datalist = deal.query_like_list_data(action, params)

            if datalist:
                # 清空隐藏块并显示查询结果
                self.hidden_list.clear()
                for item in datalist:
                    self.hidden_list.addItem(item['gn'])  # 只显示 gn（概念名称）

                # 设置浮动窗口的位置（在输入框下方）
                self.floating_window.move(
                    self.input_box.mapToGlobal(QPoint(0, self.input_box.height())).x(),
                    self.input_box.mapToGlobal(QPoint(0, self.input_box.height())).y()
                )
                self.floating_window.show()  # 显示浮动窗口
            else:
                self.floating_window.hide()  # 未查询到数据时隐藏
        else:
            self.floating_window.hide()  # 输入框为空时隐藏

    def on_list_item_clicked(self, item):
        """隐藏块项点击事件处理函数"""
        # 获取点击项的文本（gn）
        selected_gn = item.text()

        # 触发数据库查询，根据 gn 查询对应的股票数据
        action = 'like_query_gp_list'
        deal = DeaiClientData()
        datalist = deal.query_like_list_gp(action, selected_gn)

        if datalist:
            # 清空列表并加载查询结果
            self.result_list.clear()
            for item in datalist:
                # 每行显示股票代码、股票名称、概念
                list_item = QListWidgetItem(f"{item['gpdm']} - {item['gpmc']} - {item['gn']}")
                self.result_list.addItem(list_item)

            # 隐藏浮动窗口
            self.floating_window.hide()
        else:
            print("未查询到数据")

    def on_confirm_button_clicked(self):
        """确定按钮点击事件处理函数"""
        # 提取列表中的股票代码
        selected_gpdm_list = []
        for index in range(self.result_list.count()):
            item = self.result_list.item(index)
            item_text = item.text()
            gpdm = item_text.split(" - ")[0]  # 提取股票代码
            selected_gpdm_list.append(gpdm)

        if selected_gpdm_list:
            # 获取 ck_table 中表的行数
            current_row_count = self.ck_table._model.rowCount()
            total_count = current_row_count + len(selected_gpdm_list)

            if total_count > 80:
                # 超过 80 条数据，提示请删除数据，不关闭窗口
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("提示")
                msg_box.setText("列表中数据不能超过 80 条，请删除后再添加。")
                msg_box.setIcon(QMessageBox.Information)
                ok_button = msg_box.addButton("确定", QMessageBox.AcceptRole)
                ok_button.setStyleSheet("min-width: 60px; min-height: 25px; font-size: 14px;")
                msg_box.exec()
            else:
                # 没有超过 80 条数据，通过信号传递选中的股票代码，关闭当前窗口
                self.stock_codes_selected.emit(selected_gpdm_list)
                self.close()
        else:
            print("未选择任何股票代码")

    def delete_selected_items(self):
        """删除选中的行"""
        selected_items = self.result_list.selectedItems()
        if selected_items:
            for item in selected_items:
                self.result_list.takeItem(self.result_list.row(item))  # 删除选中的行
        else:
            print("未选择任何行")


