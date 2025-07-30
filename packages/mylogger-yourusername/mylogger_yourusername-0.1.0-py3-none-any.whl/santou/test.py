from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from santou.DeaiClientData import DeaiClientData



class view(QTableView):
    def __init__(self):
        super(view, self).__init__()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
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


class model_(QStandardItemModel):
    def __init__(self, view, username):
        super(model_, self).__init__()
        self._view = view
        self.username = username
        self.setHorizontalHeaderLabels(["设置为默认", "QMT地址", "账户", "删除", "id"])
        self.list_row()

        # 连接itemChanged信号处理复选框单选逻辑
        self.itemChanged.connect(self.handle_item_changed)

    def handle_item_changed(self, item):
        """处理复选框状态变化实现单选"""
        if item.column() == 0:  # 只处理第一列的变化
            if item.checkState() == Qt.CheckState.Checked:
                # 遍历所有行取消其他复选框的选中状态
                for row in range(self.rowCount()):
                    if row != item.row():
                        other_item = self.item(row, 0)
                        other_item.setCheckState(Qt.CheckState.Unchecked)

    def list_row(self):
        """从数据库获取列表数据"""
        deal = DeaiClientData()
        data_list = deal.get_account_data("get_account_data", self.username)
        if data_list:
            for item in data_list:
                self.add_row([item["dz"], item["account"], "", item["id"]])
        self._view.setColumnHidden(4, True)

    def add_row(self, data):
        """添加一行数据"""
        checkbox_item = QStandardItem()
        checkbox_item.setCheckable(True)
        checkbox_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox_item.setCheckState(Qt.CheckState.Unchecked)
        checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        checkbox_item.setSizeHint(QSize(30, 30))

        row_items = [checkbox_item]
        for text in data:
            item = QStandardItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            row_items.append(item)

        self.appendRow(row_items)

    def delete_row(self, row):
        if 0 <= row < self.rowCount():
            self.removeRow(row)


class table_list_acc(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setStyleSheet("QWidget { margin: 0px; padding: 0px; }")
        self.init_ui()

    def init_ui(self):
        self._view = view()
        self._model = model_(self._view, self.username)
        self._view.setModel(self._model)
        self._view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._view.setContentsMargins(0, 0, 0, 0)
        self._view.setColumnWidth(0, 80)
        self._view.setColumnWidth(1, 300)
        self._view.setColumnWidth(2, 150)
        self._view.setColumnWidth(3, 100)
        self._view.setFixedWidth(770)

        hbox = QHBoxLayout()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(hbox)
        main_layout.addWidget(self._view)

        self.add_buttons_to_table()

    def add_buttons_to_table(self):
        """为每行添加删除按钮"""
        for row in range(self._model.rowCount()):
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn = QPushButton("删 除")
            btn.setFixedSize(80, 20)
            row_id = self._model.item(row, 4).text()
            btn.clicked.connect(lambda _, id=row_id: self.delete_account(id))

            layout.addWidget(btn)
            self._view.setIndexWidget(self._model.index(row, 3), widget)

    def delete_account(self, account_id):
        confirm = QMessageBox(self)
        confirm.setWindowTitle("确认删除")
        confirm.setText("确定要删除该记录吗？")
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm.button(QMessageBox.Yes).setText("确定")
        confirm.button(QMessageBox.No).setText("取消")

        if confirm.exec() == QMessageBox.Yes:
            deal = DeaiClientData()
            if deal.delete_account_data("delete_account_data", account_id).get("message") == "success":
                self.refresh_table()
                QMessageBox.information(self, "成功", "删除成功！")
            else:
                QMessageBox.warning(self, "失败", "删除失败！")

    def refresh_table(self):
        """刷新表格数据"""
        self._model.clear()
        self._model.setHorizontalHeaderLabels(["设置为默认", "QMT地址", "账户", "删除", "id"])
        self._model.list_row()
        self.add_buttons_to_table()
        self._view.setColumnHidden(4, True)