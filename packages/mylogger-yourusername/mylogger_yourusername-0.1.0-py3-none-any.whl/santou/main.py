from santou.account import Account
from santou.cebianlan.AccountInfoDialog import AccountInfoDialog
from santou.gjqmt.qmt_zh import QMTConnection
from santou.db_tool.db_ym1 import db_ym1
from santou.sell.sell_list_table import sell_list_table
import threading
import time
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy, QMainWindow, QTabWidget,
    QApplication, QDialog, QTextEdit, QScrollArea, QMessageBox,
    QHBoxLayout, QLabel  # 导入必要的布局和控件
)
import sys
import os
import webbrowser
from santou.tjdmr.tjd_ym import tjd_ym
from santou.logging.log import logger
from santou.path import path

class WorkerThread(threading.Thread):
    """
    后台线程类，模拟一个长时间运行的任务
    """

    def __init__(self):
        super().__init__()
        self._is_running = True  # 控制线程运行的标志

    def run(self):
        """
        线程运行的主逻辑
        """
        while self._is_running:
            # print("后台线程运行中...")
            time.sleep(1)

    def stop(self):
        """
        停止线程
        """
        self._is_running = False
        print("后台线程已停止")


# 打板1选项卡
class dbWidget1(QWidget):
    def __init__(self):
        super(dbWidget1, self).__init__()
        # 显示 table 列表
        layout = QVBoxLayout(self)  # 使用垂直布局
        layout.setContentsMargins(0, 0, 0, 0)
        self.db_ym1 = db_ym1()  # 实例化 Windowtable
        # 设置大小策略为扩展，使其能够自适应父容器大小
        self.db_ym1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.db_ym1)  # 将 Windowtable 添加到布局中
        self.setLayout(layout)  # 设置布局


# 条件单买入选项卡
class tjdWidget(QWidget):
    def __init__(self):
        super(tjdWidget, self).__init__()
        # 显示 table 列表
        layout = QVBoxLayout(self)  # 使用垂直布局
        layout.setContentsMargins(0, 0, 0, 0)
        self.tjd_ym = tjd_ym()  # 实例化 Windowtable
        # 设置大小策略为扩展，使其能够自适应父容器大小
        self.tjd_ym.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tjd_ym)  # 将 Windowtable 添加到布局中
        self.setLayout(layout)  # 设置布局


# 选项卡
class TestWidget(QWidget):
    def __init__(self):
        super(TestWidget, self).__init__()
        # 显示 table 列表
        layout = QVBoxLayout(self)  # 使用垂直布局
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)  # 设置布局


# 组合条件单卖出
class TestWidget_Sell(QWidget):
    def __init__(self):
        super(TestWidget_Sell, self).__init__()
        # 显示 table 列表
        layout = QVBoxLayout(self)  # 使用垂直布局
        layout.setContentsMargins(0, 0, 0, 0)
        self.sell_list = sell_list_table()  # 实例化 Windowtable
        # 设置大小策略为扩展，使其能够自适应父容器大小
        self.sell_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.sell_list)  # 将 Windowtable 添加到布局中
        self.setLayout(layout)  # 设置布局




class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.base_dir = path().get_base_path()  # 获取基础路径

        photo_path = os.path.join(self.base_dir, 'photo', 'title_top.png')

        self.setWindowIcon(QIcon(photo_path))
        self.setWindowTitle("量化赢家1.0            联系我们： QQ：366310986       微信：trader_win_123")
        # 加载账户信息
        Account()

        # 禁用最大化按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        self.worker_thread = WorkerThread()  # 创建后台线程
        self.worker_thread.start()  # 启动后台线程
        self.window_ui()

    def window_ui(self):
        # 工具栏
        tool = self.addToolBar("持仓")
        tool.setMovable(False)  # 允许工具栏拖动
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, tool)  # 将工具栏添加到左侧
        # 修改后

        photo_pathc = os.path.join(self.base_dir, 'photo', 'connect.png')
        con = tool.addAction(QIcon(photo_pathc), "联系我们")
        con.triggered.connect(self.show_connect_info)  # 添加连接
        tool.addSeparator()
        photo_path1 = os.path.join(self.base_dir, 'photo', 'title.png')
        zhxx = tool.addAction(QIcon(photo_path1), "账户信息")
        zhxx.triggered.connect(self.show_account_info)  # 添加连接
        tool.addSeparator()
        sysm_path1 = os.path.join(self.base_dir, 'photo', 'sysm.png')
        sysm = tool.addAction(QIcon(sysm_path1), "使用说明")
        sysm.triggered.connect(self.show_sysm_info)  # 添加连接
        tool.addSeparator()
        photo_path2 = os.path.join(self.base_dir, 'photo', 'rizi.jpeg')
        action = tool.addAction(QIcon(photo_path2), "错误日志")
        action.triggered.connect(self.show_error_log)

        tool.addSeparator()
        # tool.addAction('header2')
        tool.setIconSize(QSize(50, 50))

        # 添加选项卡
        self.tab = QTabWidget()
        # 设置选项卡的样式表，增大字体大小
        self.tab.setStyleSheet("""
            QTabBar::tab {
                color: black; /* 未选中时的字体颜色 */
                font-size: 14px; /* 调整字体大小 */
            }
            QTabBar::tab:selected {
                color: red; /* 选中时的字体颜色 */
                font-size: 14px; /* 调整字体大小 */
            }
        """)
        db11 = dbWidget1()

        test3 = TestWidget_Sell()
        tjd_ym = tjdWidget()
        # buy_amount_settings_tab = BuyAmountSettingsTab()  # 买入资金设置选项卡
        qmt = QMTConnection()
        self.tab.addTab(db11, '打板买入')
        self.tab.addTab(tjd_ym, '条件单买入')
        self.tab.addTab(test3, '条件单卖出')
        self.tab.addTab(qmt, '交易连接设置')
        self.tab.setMovable(True)
        self.tab.setTabToolTip(1, 'hello world')
        self.tab.setTabsClosable(False)

        # 底部窗口、
        # self.bottom_widget = QLabel("这是底部窗口内容")
        # self.bottom_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 设置中央部件
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)  # 垂直布局
        layout.addWidget(self.tab)  # 添加选项卡
        # layout.addWidget(self.bottom_widget)  # 添加底部窗口
        self.setCentralWidget(central_widget)  # 设置为主窗口的中央部件

    def show_error_log(self):
        log_file_path = os.path.join(self.base_dir, 'photo', 'app.log')
        try:
            with open(log_file_path, 'r', encoding='utf-8') as file:
                log_content = file.read()
            log_dialog = LogDialog(log_content)
            log_dialog.exec()
        except FileNotFoundError:
            logger.error('main:show_error_log发生异常', exc_info=True)
            QMessageBox.warning(self, "错误", "未找到 app.log 文件。")

    def closeEvent(self, event):
        """
        重写 closeEvent 方法，在窗口关闭时执行清理操作
        """
        print("窗口关闭，执行清理操作...")
        self.worker_thread.stop()  # 停止后台线程
        self.worker_thread.join()  # 等待线程结束
        event.accept()  # 接受关闭事件

    def show_account_info(self):
        """显示账户信息对话框"""
        dialog = AccountInfoDialog()
        dialog.exec()

    def show_sysm_info(self):
        """直接打开使用说明文档，不在窗口中加载"""
        docx_path = os.path.join(self.base_dir,"photo",'量化赢家使用说明.docx')

        if os.path.exists(docx_path):
            try:
                # 直接使用默认程序打开文档
                webbrowser.open(docx_path)
            except Exception as e:
                logger.error('main:show_sysm_info:发生错误：', exc_info=True)
                QMessageBox.warning(self, "错误", f"打开文档失败: {str(e)}")
        else:
            QMessageBox.warning(self, "未找到文件", "未找到量化赢家使用说明.docx 文件。")

    def show_connect_info(self):
        """显示联系信息对话框"""
        dialog = ConnectInfoDialog(self.base_dir)
        dialog.exec()


class LogDialog(QDialog):
    def __init__(self, log_content):
        super().__init__()
        self.setWindowTitle("错误日志")
        self.base_dir = path().get_base_path()  # 获取基础路径
        photo_path = os.path.join(self.base_dir, 'photo', 'title_top.png')
        self.setWindowIcon(QIcon(photo_path))
        self.setFixedWidth(700)
        self.setFixedHeight(500)
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setFixedWidth(700)
        text_edit.setFixedHeight(500)
        text_edit.setPlainText(log_content)
        text_edit.setReadOnly(True)
        scroll_area = QScrollArea()
        scroll_area.setWidget(text_edit)
        layout.addWidget(scroll_area)
        self.setLayout(layout)


class ConnectInfoDialog(QDialog):
    def __init__(self, base_dir):
        super().__init__()
        self.setWindowTitle("联系我们")
        self.base_dir = path().get_base_path()
        self.setWindowIcon(QIcon(os.path.join(self.base_dir,"photo", 'title_top.png')))
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




