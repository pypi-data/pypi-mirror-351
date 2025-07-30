import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QGroupBox, QLineEdit,
    QVBoxLayout, QHBoxLayout, QLabel, QDateEdit,
    QPushButton, QComboBox, QMessageBox
)
from PySide6.QtCore import QDate
from power.DeaiClientData import DeaiClientData


class InputWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.id = None
        # 绑定按钮事件
        self.query_btn.clicked.connect(self.on_query)
        # 绑定新增按钮事件
        self.add_wechat_btn.clicked.connect(self.on_add_wechat)
        self.add_qq_btn.clicked.connect(self.on_add_qq)
        self.save_code_btn.clicked.connect(self.on_save_code)
        self.save_date_btn.clicked.connect(self.on_save_date)

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()

        # ===== 查询条件区域 =====
        query_group = QGroupBox("查询条件")
        query_layout = QVBoxLayout()

        # 微信 ID 输入
        wechat_layout = QHBoxLayout()
        wechat_layout.addWidget(QLabel("微信 ID："))
        self.wechat_input = QLineEdit()
        wechat_layout.addWidget(self.wechat_input)

        # QQ 账号输入
        qq_layout = QHBoxLayout()
        qq_layout.addWidget(QLabel("QQ 账号："))
        self.qq_input = QLineEdit()
        qq_layout.addWidget(self.qq_input)

        # 校验码输入
        code_layout = QHBoxLayout()
        code_layout.addWidget(QLabel("软件唯一校验码："))
        self.code_input = QLineEdit()
        code_layout.addWidget(self.code_input)

        # 查询按钮（必须存在的关键部分）
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.query_btn = QPushButton("查询")  # 创建查询按钮
        btn_layout.addWidget(self.query_btn)

        # 组装查询区域
        query_layout.addLayout(wechat_layout)
        query_layout.addLayout(qq_layout)
        query_layout.addLayout(code_layout)
        query_layout.addLayout(btn_layout)
        query_group.setLayout(query_layout)

        # ===== 查询结果展示区域 =====
        result_group = QGroupBox("查询结果")
        result_layout = QVBoxLayout()

        # 微信 ID 展示
        result_wechat = QHBoxLayout()
        result_wechat.addWidget(QLabel("微信 ID："))
        self.result_wechat = QLabel("")
        result_wechat.addWidget(self.result_wechat)

        # QQ 账号展示
        result_qq = QHBoxLayout()
        result_qq.addWidget(QLabel("QQ 账号："))
        self.result_qq = QLabel("")
        result_qq.addWidget(self.result_qq)

        # 校验码展示
        result_code = QHBoxLayout()
        result_code.addWidget(QLabel("软件唯一校验码："))
        self.result_code = QLabel("")
        result_code.addWidget(self.result_code)

        # 登录日期展示
        result_date = QHBoxLayout()
        result_date.addWidget(QLabel("登录日期："))
        self.result_date = QLabel("")
        result_date.addWidget(self.result_date)

        # 起始日期展示
        result_start = QHBoxLayout()
        result_start.addWidget(QLabel("起始日期："))
        self.result_start = QLabel("")
        result_start.addWidget(self.result_start)

        # 结束日期展示
        result_end = QHBoxLayout()
        result_end.addWidget(QLabel("结束日期："))
        self.result_end = QLabel("")
        result_end.addWidget(self.result_end)

        # 行情展示
        result_market = QHBoxLayout()
        result_market.addWidget(QLabel("行情："))
        self.result_market = QLabel("")
        result_market.addWidget(self.result_market)

        # 组装结果区域
        result_layout.addLayout(result_wechat)
        result_layout.addLayout(result_qq)
        result_layout.addLayout(result_code)
        result_layout.addLayout(result_date)
        result_layout.addLayout(result_start)
        result_layout.addLayout(result_end)
        result_layout.addLayout(result_market)
        result_group.setLayout(result_layout)

        # ===== 详细信息区域 =====
        detail_group = QGroupBox("详细信息")
        detail_layout = QVBoxLayout()

        # 微信 ID 输入
        wechat2_layout = QHBoxLayout()
        wechat2_layout.addWidget(QLabel("微信 ID："))
        self.wechat2_input = QLineEdit()
        wechat2_layout.addWidget(self.wechat2_input)
        self.add_wechat_btn = QPushButton("添加微信ID")
        wechat2_layout.addWidget(self.add_wechat_btn)

        # QQ 账号输入
        qq2_layout = QHBoxLayout()
        qq2_layout.addWidget(QLabel("QQ 账号："))
        self.qq2_input = QLineEdit()
        qq2_layout.addWidget(self.qq2_input)
        self.add_qq_btn = QPushButton("添加 QQ 账号")
        qq2_layout.addWidget(self.add_qq_btn)

        # 校验码输入
        code2_layout = QHBoxLayout()
        code2_layout.addWidget(QLabel("软件唯一校验码："))
        self.code2_input = QLineEdit()
        code2_layout.addWidget(self.code2_input)
        self.save_code_btn = QPushButton("保存")
        code2_layout.addWidget(self.save_code_btn)

        # 日期范围选择
        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("起始日期："))
        self.start_date = QDateEdit()
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.start_date)

        date_range_layout.addWidget(QLabel("结束日期："))
        self.end_date = QDateEdit()
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.end_date)
        self.save_date_btn = QPushButton("保存日期")
        date_range_layout.addWidget(self.save_date_btn)

        # 行情下拉框
        market_layout = QHBoxLayout()
        market_layout.addWidget(QLabel("行情："))
        self.market_combo = QComboBox()
        self.market_combo.addItems(["3s", "0.9s", "0.6s", "0.3s"])
        market_layout.addWidget(self.market_combo)

        # 保存行情按钮
        self.save_market_btn = QPushButton("保存行情")
        market_layout.addWidget(self.save_market_btn)
        self.save_market_btn.clicked.connect(self.on_save_market)

        # 组装详细信息区域
        detail_layout.addLayout(wechat2_layout)
        detail_layout.addLayout(qq2_layout)
        detail_layout.addLayout(code2_layout)
        detail_layout.addLayout(date_range_layout)
        detail_layout.addLayout(market_layout)
        detail_group.setLayout(detail_layout)

        # 主布局组装
        main_layout.addWidget(query_group)
        main_layout.addWidget(result_group)
        main_layout.addWidget(detail_group)

        self.setLayout(main_layout)
        self.setWindowTitle('量化赢家权限管理系统')
        self.resize(600, 600)

    def on_query(self):
        """查询按钮点击事件"""
        wechat = self.wechat_input.text()
        qq = self.qq_input.text()
        code = self.code_input.text()

        action = "query_username_power"
        deal = DeaiClientData()
        message = deal.query_username_power(action, wechat, qq, code)
        print(f"me:{message}")
        message = message[0]
        # 更新结果展示
        self.id = message["id"]
        self.result_wechat.setText(message["wechat"])
        self.result_qq.setText(message["qq"])
        self.result_code.setText(message["acc"])
        self.result_date.setText(message["dl_date"])
        self.result_start.setText(message["start_rq"])
        self.result_end.setText(message["end_rq"])
        self.result_market.setText(message["zh_lx"])

        print("\n=== 执行查询 ===")
        print(f"查询条件 - 微信 ID: {wechat}")
        print(f"查询条件 - QQ 账号: {qq}")
        print(f"查询条件 - 校验码: {code}")

    def on_save(self):
        """保存按钮点击事件"""
        print("\n=== 保存配置 ===")
        print(f"详细信息 - 微信 ID: {self.wechat2_input.text()}")
        print(f"详细信息 - QQ 账号: {self.qq2_input.text()}")
        print(f"详细信息 - 校验码: {self.code2_input.text()}")
        print(f"日期范围: {self.start_date.date().toString('yyyy-MM-dd')} 至 "
              f"{self.end_date.date().toString('yyyy-MM-dd')}")
        print(f"详细信息 - 行情: {self.market_combo.currentText()}")

    def on_add_wechat(self):
        """添加微信 ID 按钮点击事件"""
        wechat = self.wechat2_input.text()
        action="add_wechat"
        message = DeaiClientData().add_wechat(action, wechat,self.id)
        print(message)
        if message["message"]=="success":
            QMessageBox.information(
                self,
                "保存成功",
                "微信 ID 保存成功！",
                QMessageBox.Ok
            )

    def on_add_qq(self):
        """添加 QQ 账号按钮点击事件"""
        qq = self.qq2_input.text()
        action = "add_qq"
        message = DeaiClientData().add_qq(action, qq, self.id)
        if message["message"] == "success":
            QMessageBox.information(
                self,
                "保存成功",
                "qq保存成功！",
                QMessageBox.Ok
            )

    def on_save_code(self):
        """保存校验码按钮点击事件"""
        code = self.code2_input.text()
        action = "add_acc"
        message = DeaiClientData().add_acc(action, code, self.id)

        if message["message"] == "success":
            QMessageBox.information(
                self,
                "保存成功",
                "软件唯一校验码保存成功！",
                QMessageBox.Ok
            )

    def on_save_date(self):
        """保存日期按钮点击事件"""
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        action = "add_rq"
        message = DeaiClientData().add_rq(action, start_date,end_date,self.id)

        if message["message"] == "success":
            QMessageBox.information(
                self,
                "保存成功",
                "有效期权限保存成功！",
                QMessageBox.Ok
            )

    def on_save_market(self):
        """保存行情按钮点击事件"""
        market = self.market_combo.currentText()
        action = "add_zh_lx"
        message = DeaiClientData().add_zh_lx(action, market, self.id)

        if message["message"] == "success":
            QMessageBox.information(
                self,
                "保存成功",
                "行情保存成功！",
                QMessageBox.Ok
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InputWindow()
    window.show()
    sys.exit(app.exec())