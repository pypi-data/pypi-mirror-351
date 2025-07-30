
import threading

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import QMessageBox
from santou.DeaiClientData import DeaiClientData
from santou.tjdmr_list.AddStockDialog import AddStockDialog
from santou.tjdmr_list.FileDialog import FileSelectionDialog
from santou.tjdmr_list.cx import Ck

def get_button_style():
    """Returns the style for the buttons."""
    return """
        QPushButton {
            background-color: #3498db;  /* 按钮背景色 */
            color: white;              /* 按钮文字颜色 */
            font-size: 15px;           /* 按钮字体大小 */
            border: none;              /* 去掉边框 */
            border-radius: 5px;        /* 圆角边框 */
        }
       
        QPushButton:pressed {
            background-color: #FFCCCB; /* 按下时的背景色 */
        }
    """


def get_black_button_style():
    """Returns the style for the black buttons (clear and delete)."""
    return """
        QPushButton {
            background-color: black;  /* 按钮背景色 */
            color: white;              /* 按钮文字颜色 */
            font-size: 15px;           /* 按钮字体大小 */
            border: none;              /* 去掉边框 */
            border-radius: 5px;        /* 圆角边框 */
        }

        QPushButton:pressed {
            background-color: #FFCCCB; /* 按下时的背景色 */
        }
    """
class view(QTableView):
    def __init__(self):
        super(view, self).__init__()
        # 设置列宽调整模式
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)  # 列宽可手动调整
        self.setFrameShape(QFrame.Shape.NoFrame)  # 移除边框
        self.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置行号居中对齐
        self.setStyleSheet("""
            QHeaderView::section {
                font-weight: bold;
                border: none;
                top:0px;
                background-color:  #E0E6ED;
            }
            QTableCornerButton::section {
                border: none;
            }
        """)

    def viewportEvent(self, event):
        if event.type() == QEvent.ToolTip:
            # 获取鼠标指针所在的位置
            pos = event.pos()
            # 获取单元格索引
            index = self.indexAt(pos)
            if index.isValid():
                # 获取单元格内容
                content = index.data(Qt.DisplayRole)
                if content:
                    # 立即显示提示框
                    QToolTip.showText(event.globalPos(), content, self.viewport())
            else:
                QToolTip.hideText()  # 鼠标不在有效单元格时隐藏提示框
            return True
        return super(view, self).viewportEvent(event)


class model_(QStandardItemModel):
    def __init__(self, view,db_ym1):
        super(model_, self).__init__()
        self._view = view  # 将传入的 view 绑定到 model_ 的 _view 属性
        self.db_ym1=db_ym1
        self.setHorizontalHeaderLabels(
            ["选择", "股票名称", "代码", "现价", "涨幅","换手率", "昨涨停板数", "流通市值（亿）","昨收盘价","流通股本","昨收盘价"]
        )

    def list_row(self, params):

        """从数据库获取列表数据"""
        deal = DeaiClientData()
        action = "list_gp_data"
        data_list = deal.list_gp_data(action, params)
        existing_codes = set()
        for row in range(self.rowCount()):
            code_item = self.item(row, 2)
            if code_item:
                existing_codes.add(code_item.text())

        if data_list:
            for item in data_list:

                code = item["gpdm"]
                if code in existing_codes:
                    continue
                self.add_row([item["gpmc"], item["gpdm"], item["xj"], "", "", item['ztzt'], item['ltsz'],
                              item["close_pre_day_price"], item["ltgbnum"], item["xj"]])



                existing_codes.add(code)
        self._view.setColumnHidden(8, True)
        self._view.setColumnHidden(9, True)
        self._view.setColumnHidden(10, True)

        #更新涨幅和换手率
        threading.Thread(target=self.db_ym1.phsj_timer).start()

    def add_row(self, data):
        """添加一行数据"""
        checkbox_item = QStandardItem()
        checkbox_item.setCheckable(True)  # 设置复选框
        checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置居中对齐
        checkbox_item.setCheckState(Qt.CheckState.Unchecked)  # 默认未选中
        checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

        # 添加数据到其他列
        row_items = [checkbox_item]  # 先添加复选框单元格
        for text in data:
            item = QStandardItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置居中对齐
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            row_items.append(item)
        self.appendRow(row_items)




class Windowtable(QWidget):
    def __init__(self,db_ym1):
        super(Windowtable, self).__init__()
        # 设置样式表去除内边距
        self.db_ym1 = db_ym1
        self.setStyleSheet("QWidget { margin: 0px; padding: 0px; }")
        self.window_ui()
        # 等待页面布局完成后启动定时器
        QTimer.singleShot(0, self.start_periodic_update)

    def start_periodic_update(self):
        # 确保所有布局事件处理完毕
        QApplication.processEvents()

        # 初始化定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_table_periodically)
        # 8 小时的毫秒数：8 * 60 * 60 * 1000
        self.timer.start( 10 * 60 * 60 *1000)

    def update_table_periodically(self):
        # 检查表格是否为空
        if self._model.rowCount() == 0:
            return
        # 初始化一个空列表，用于存储表格中第三列的股票代码
        codes = []
        # 遍历模型中的每一行
        for row in range(self._model.rowCount()):
            # 获取当前行第三列（索引为 2）的项
            code_item = self._model.item(row, 2)
            # 检查该项是否存在
            if code_item:
                # 如果存在，将该项的文本（即股票代码）添加到 codes 列表中
                codes.append(code_item.text())
        # 去重处理
        codes = list(set(codes))
        # 调用模型的 list_row 方法，传入获取到的股票代码列表，更新表格数据
        list_row_thread = threading.Thread(target=self._model.list_row, args=(codes,))
        list_row_thread.start()


    def window_ui(self):
        """初始化界面"""

        # 创建视图和模型
        self._view = view()
        self._model = model_(self._view,self.db_ym1)
        self._view.setModel(self._model)
        self._view.setSelectionMode(QAbstractItemView.MultiSelection)  # 支持多选
        self._view.setSelectionBehavior(QAbstractItemView.SelectRows)  # 选中整行
        self._view.setContentsMargins(0, 0, 0, 0)
        self._view.setColumnWidth(0, 20)  # 将第一列宽度设置为 50 像素
        self._view.setColumnWidth(1, 80)
        self._view.setColumnWidth(2, 80)
        self._view.setColumnWidth(3, 50)
        self._view.setColumnWidth(4, 50)
        self._view.setColumnWidth(5, 50)
        self._view.setColumnWidth(6, 80)
        self._view.setColumnWidth(7, 100)
        self._view.setColumnWidth(8, 80)
        self._view.setColumnHidden(8, True)
        self._view.setColumnHidden(9, True)
        self._view.setColumnHidden(10, True)

        # 创建主布局
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)  # 去掉边距
        hbox.setSpacing(5)  # 设置按钮之间的间距

        # 添加“全选”按钮
        self.select_all_button = QPushButton("全 选")
        self.select_all_button.setStyleSheet(get_black_button_style())
        self.select_all_button.setFixedSize(50, 25)
        self.select_all_button.clicked.connect(self.select_all_rows)  # 绑定全选事件
        hbox.addWidget(self.select_all_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # 添加“取消选中”按钮
        self.unselect_all_button = QPushButton("取消选中")
        self.unselect_all_button.setFixedSize(70, 25)
        self.unselect_all_button.setStyleSheet(get_black_button_style())
        self.unselect_all_button.clicked.connect(self.unselect_all_rows)  # 绑定取消选中事件
        hbox.addWidget(self.unselect_all_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # 添加“删除”按钮
        self.delbu = QPushButton("删除选中")
        self.delbu.setFixedSize(70, 25)
        self.delbu.setStyleSheet(get_black_button_style())
        self.delbu.clicked.connect(self.delete_selected_rows)  # 绑定删除行事件
        hbox.addWidget(self.delbu, alignment=Qt.AlignmentFlag.AlignLeft)

        # 添加“清空”按钮
        self.clear_button = QPushButton("清 空")
        self.clear_button.setFixedSize(60, 25)
        self.clear_button.setStyleSheet(get_black_button_style())
        self.clear_button.clicked.connect(self.clear_all_rows)  # 绑定清空事件
        hbox.addWidget(self.clear_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # 添加其他按钮
        self.cx_but = QPushButton("概念选股")
        self.cx_but.setFixedSize(80, 25)
        self.cx_but.setStyleSheet(get_button_style())
        self.cx_but.clicked.connect(self.open_cx_topic_window)  # 绑定点击事件
        hbox.addWidget(self.cx_but, alignment=Qt.AlignmentFlag.AlignLeft)

        self.ths_but = QPushButton("导入同花顺/通达信自选股")
        self.ths_but.setFixedSize(180, 25)
        self.ths_but.setStyleSheet(get_button_style())
        self.ths_but.clicked.connect(self.on_ths_button_clicked)  # 绑定同花顺按钮点击事件
        hbox.addWidget(self.ths_but, alignment=Qt.AlignmentFlag.AlignLeft)

        self.addgp_but = QPushButton("添加个股")
        self.addgp_but.setFixedSize(80, 25)
        self.addgp_but.setStyleSheet(get_button_style())
        self.addgp_but.clicked.connect(self.open_add_stock_dialog)
        hbox.addWidget(self.addgp_but, alignment=Qt.AlignmentFlag.AlignLeft)
        hbox.addStretch()

        # 创建主布局
        box = QVBoxLayout()
        box.setContentsMargins(0, 0, 0, 0)  # 去掉边距
        box.setSpacing(0)  # 设置按钮和表格之间的间距
        box.addLayout(hbox)
        box.addWidget(self._view)  # 添加表格视图
        self.setLayout(box)

    def select_all_rows(self):
        """全选按钮点击事件：选中所有行的复选框"""
        for row in range(self._model.rowCount()):
            item = self._model.item(row, 0)  # 获取第一列的复选框单元格
            if item:
                item.setCheckState(Qt.CheckState.Checked)  # 设置为选中状态

    def unselect_all_rows(self):
        """取消选中按钮点击事件：取消选中所有行的复选框"""
        for row in range(self._model.rowCount()):
            item = self._model.item(row, 0)  # 获取第一列的复选框单元格
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)  # 设置为未选中状态

    def delete_selected_rows(self):
        """删除选中复选框的行，并弹出确认框"""
        selected_rows = []
        for row in range(self._model.rowCount()):
            item = self._model.item(row, 0)  # 获取第一列的复选框单元格
            if item.checkState() == Qt.CheckState.Checked:  # 判断复选框是否选中
                selected_rows.append(row)
        if not selected_rows:
            # 创建自定义失败信息框
            fail_box = QMessageBox(self)
            fail_box.setWindowTitle("失败")
            fail_box.setText("警告, 未选中任何行，请勾选需要删除的行！")
            fail_box.setIcon(QMessageBox.Icon.Information)
            yesbutton = fail_box.addButton("关 闭", QMessageBox.ButtonRole.YesRole)
            yesbutton.setStyleSheet("min-width: 80px; min-height: 30px; font-size: 14px;")
            fail_box.setStyleSheet("""
                QLabel {
                    min-height: 40px;  /* 设置最小高度，让文本区域大一点 */
                    font-size: 14px;  /* 调整字体大小 */
                    qproperty-alignment: AlignCenter; /* 垂直和水平居中 */
                }
            """)
            fail_box.exec()
            return

        # 创建确认删除的 QMessageBox
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("确认 / 删除?")
        msg_box.setText(f"确定要删除 {len(selected_rows)} 行吗？")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStyleSheet("""
            QLabel {
                min-height: 40px;  /* 设置最小高度，让文本区域大一点 */
                font-size: 14px;  /* 调整字体大小 */
                qproperty-alignment: AlignCenter; /* 垂直和水平居中 */
            }
        """)
        # 设置按钮文本
        yes_button = msg_box.addButton("是", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("否", QMessageBox.ButtonRole.NoRole)
        yes_button.setStyleSheet("min-width: 80px; min-height: 30px; font-size: 14px;")
        no_button.setStyleSheet("min-width: 80px; min-height: 30px; font-size: 14px;")
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            # 用户点击了 "是"，删除选中的行
            for row in sorted(selected_rows, reverse=True):
                self._model.removeRow(row)
            # 创建自定义成功信息框
            success_box = QMessageBox(self)
            success_box.setWindowTitle("成功")
            success_box.setText(f"成功删除了 {len(selected_rows)} 行！")
            success_box.setIcon(QMessageBox.Icon.Information)
            yesbutton = success_box.addButton("是", QMessageBox.ButtonRole.YesRole)
            yesbutton.setStyleSheet("min-width: 80px; min-height: 30px; font-size: 14px;")
            success_box.setStyleSheet("""
                QLabel {
                    min-height: 40px;  /* 设置最小高度，让文本区域大一点 */
                    font-size: 14px;  /* 调整字体大小 */
                    qproperty-alignment: AlignCenter; /* 垂直和水平居中 */
                }
            """)
            success_box.exec()

    def open_add_stock_dialog(self):
        """打开添加股票对话框"""
        self.add_stock_dialog = AddStockDialog(self)
        self.add_stock_dialog.exec()

    def update_table_with_stocks(self, stock_codes):
        """使用提取到的股票代码更新表格，并确保不出现重复的股票代码"""
        if stock_codes:
            # 获取当前表格中已有的股票代码
            existing_codes = set()
            for row in range(self._model.rowCount()):
                code_item = self._model.item(row, 2)  # 假设股票代码在第 2 列
                if code_item:
                    existing_codes.add(code_item.text())
            old_sj=self._model.rowCount()
            # 过滤掉已经存在的股票代码
            new_codes = [code for code in stock_codes if code not in existing_codes]

            if new_codes:
                # 将新的股票代码添加到表格中
                len_data=old_sj+len(new_codes)
                if len_data<=80:

                    list_row_thread = threading.Thread(target=self._model.list_row, args=(new_codes,))
                    list_row_thread.start()
                else:
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("提示")
                    msg_box.setText("列表中数据不能超过80条，请删除后再添加。")
                    msg_box.setIcon(QMessageBox.Information)
                    # 设置按钮文本为中文，并调整按钮大小
                    ok_button = msg_box.addButton("确定", QMessageBox.AcceptRole)
                    ok_button.setStyleSheet("min-width: 60px; min-height: 25px; font-size: 14px;")
                    msg_box.exec()
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("提示")
                msg_box.setText("所有股票代码已存在，勿添加重复数据。")
                msg_box.setIcon(QMessageBox.Information)
                # 设置按钮文本为中文，并调整按钮大小
                ok_button = msg_box.addButton("确定", QMessageBox.AcceptRole)
                ok_button.setStyleSheet("min-width: 60px; min-height: 25px; font-size: 14px;")
                msg_box.exec()



    def update_table_with_stock_codes(self, stock_codes):
        """使用提取到的股票代码更新表格，并确保不出现重复的股票代码"""
        if stock_codes:
            # 获取当前表格中已有的股票代码
            existing_codes = set()
            for row in range(self._model.rowCount()):
                code_item = self._model.item(row, 2)  # 假设股票代码在第 2 列
                if code_item:
                    existing_codes.add(code_item.text())
            old_sj=self._model.rowCount()
            # 过滤掉已经存在的股票代码
            new_codes = [code for code in stock_codes if code not in existing_codes]

            if new_codes:
                # 将新的股票代码添加到表格中
                len_data=old_sj+len(new_codes)
                if len_data<=80:
                    #ck.close()
                    list_row_thread = threading.Thread(target=self._model.list_row, args=(new_codes,))
                    list_row_thread.start()

                else:
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("提示")
                    msg_box.setText("列表中数据不能超过80条，请删除后再添加。")
                    msg_box.setIcon(QMessageBox.Information)
                    # 设置按钮文本为中文，并调整按钮大小
                    ok_button = msg_box.addButton("确定", QMessageBox.AcceptRole)
                    ok_button.setStyleSheet("min-width: 60px; min-height: 25px; font-size: 14px;")
                    msg_box.exec()
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("提示")
                msg_box.setText("所有股票代码已存在，勿添加重复数据。")
                msg_box.setIcon(QMessageBox.Information)
                # 设置按钮文本为中文，并调整按钮大小
                ok_button = msg_box.addButton("确定", QMessageBox.AcceptRole)
                ok_button.setStyleSheet("min-width: 60px; min-height: 25px; font-size: 14px;")
                msg_box.exec()

    #概念选股
    def open_cx_topic_window(self):
        """打开查询窗口"""
        self.create_topic_window = Ck(self)
        self.create_topic_window.stock_codes_selected.connect(self.update_table_with_stock_codes)
        self.create_topic_window.show()

    def on_ths_button_clicked(self):
        """弹出文件选择对话框"""
        self.dialog = FileSelectionDialog(self)
        self.dialog.stock_codes_extracted.connect(self.update_table_with_stock_codes)
        self.dialog.exec()

    def clear_all_rows(self):
        """清空表格中的所有数据"""
        # 检查表格是否为空
        # 创建确认清空的 QMessageBox
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("确认 / 清空?")
        msg_box.setText("确定要清空表格中的所有数据吗？")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStyleSheet("""
            QLabel {
                min-height: 40px;  /* 设置最小高度，让文本区域大一点 */
                font-size: 14px;  /* 调整字体大小 */
                qproperty-alignment: AlignCenter; /* 垂直和水平居中 */
            }
        """)
        # 设置按钮文本
        yes_button = msg_box.addButton("是", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("否", QMessageBox.ButtonRole.NoRole)
        yes_button.setStyleSheet("min-width: 80px; min-height: 30px; font-size: 14px;")
        no_button.setStyleSheet("min-width: 80px; min-height: 30px; font-size: 14px;")
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            # 用户点击了 "是"，清空表格中的所有数据
            self._model.removeRows(0, self._model.rowCount())


