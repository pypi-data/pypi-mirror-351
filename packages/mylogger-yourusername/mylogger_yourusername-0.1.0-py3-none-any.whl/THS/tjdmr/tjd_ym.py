from santou.tjdmr_list.ck_table import *
from santou.tjdmr.tjd_db import tjd_db
from santou.tjdmr.moneySeparatedLineEdit import moneySeparatedLineEdit
from santou.qmt_trader import qmt_trader
from datetime import datetime
from PySide6.QtWidgets import  QWidget,  QSpinBox, QLabel
from santou.DeaiClientData import DeaiClientData
from PySide6.QtWidgets import (
    QVBoxLayout, QMessageBox
)
from concurrent.futures import ThreadPoolExecutor
from santou.tjdmr.TimeSpinBox import TimeSpinBox
from santou.save_qmt import save_qmt
from santou.tjdmr.LittleSwitchButton import LittleSwitchButton
from santou.tjdmr.mranniu import SwitchButton
from santou.account import Account
import threading
import os
from  santou.trading_time import ChinaHolidays
import re
from datetime import date
import json
from santou.path import path
import time
from santou.tjdmr.yzTool import yzTool
from santou.logging.log import logger
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



class ConnectionResultSignal(QObject):
    result_signal = Signal(dict)


class tjd_ym(QMainWindow):

    # 定义一个信号，用于通知主界面刷新列表
    save_cele_success = Signal()
    #获取打了几个板了数据
    update_zxzt_total = Signal(int)  # 新增信号

    #更新提示框
    tsk = Signal()
    # 添加更新股票数据的信号
    stock_data_updated = Signal(dict)  # 新增信号
    # 新增信号用于传递组合框数据
    combo_data_ready = Signal(list)  # 添加这个信号
    # 新增信号用于传递数据库加载数据
    db1_data_ready = Signal(dict)  # 新增信号

    # 金额不足提示
    jebz_info = Signal(dict)  # 新增信号
    yebz_code = []
    def __init__(self):
        super().__init__()
        # 设置窗口标题和大小
        self.qmt_trader = None
        self.setWindowTitle("打板页面")
        #self.setFixedSize(1050, 710)
        self.db1=None
        self.trader = None
        self.update_thread = None  # 用于存储更新线程
        self.username=Account.username
        #储存余额不足的票，只让他提示一次

        self.thread_pool = ThreadPoolExecutor(max_workers=10)  # 创建线程池，可根据实际情况调整最大工作线程数
        #获取打了几个板了信号槽
        self.update_zxzt_total.connect(self.set_dbsm2_text)  # 连接信号到槽
        self.stock_data_updated.connect(self.handle_stock_data_update)  # 连接信号到槽


        # 连接信号到槽函数
        self.combo_data_ready.connect(self.update_combo_box)
        # 连接信号到槽函数
        self.db1_data_ready.connect(self.handle_db1_data)
        self.username = Account().get_username()
        self.zh_lx = Account.zh_lx

        # 创建主布局（垂直排列）
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)  # 设置主布局的间距为 10 像素
        main_layout.setContentsMargins(0, 0, 0, 0)  # 设置主布局的边距为 0

        # 创建顶部页面
        top_page = self.create_top_page()
        main_layout.addWidget(top_page)

        # 创建按钮布局（五个横向排列的按钮）
        button_layout = self.create_button_layout()
        main_layout.addLayout(button_layout)

        # 创建底部页面（横向排列）
        bottom_pages = self.create_bottom_pages()
        main_layout.addWidget(bottom_pages)

        # 设置主布局
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 初始化时设置输入框状态
        self.disable_price_inputs()  # 初始禁用股价输入框
        self.disable_hsl_inputs()  # 初始禁用换手率输入框

        # 初始化一个空列表来存储代码
        self.table = []  # 假设这是从外部获取的表格数据
        self.codes_list = []  # 用于存储从 table 中提取的代码

        #盘中实时数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_codes_list)
        self.timer.start(Account().get_time())

        #按钮变色
        self.button_timer = QTimer(self)
        self.button_timer.timeout.connect(self.toggle_button_color)

        # 连接输入框的验证信号
        # 连接输入框的验证信号
        self.zf_min.editingFinished.connect(self.validate_zf_min)
        self.zf_max.editingFinished.connect(self.validate_zf_max)
        self.yfzzf_min.editingFinished.connect(self.validate_yfzzf_min)
        self.yfzzf_max.editingFinished.connect(self.validate_yfzzf_max)
        self.price_min.editingFinished.connect(self.validate_price_min)
        self.price_max.editingFinished.connect(self.validate_price_max)

    def jebz_info_add(self,params):
        code=params["stock_code"]
        #不存在才提示，存在就不用重复提示了
        if code not in tjd_ym.yebz_code:
            tjd_ym.yebz_code.append(code)
            action = 'save_cj_data'
            deal = DeaiClientData()
            cj_status="0"
            czlx="tjd"
            re = deal.save_cj_data(action, params, self.username, cj_status, czlx)
            if re["message"] == "success":
                # 通知更新提示框
                self.tsk.emit()

    def validate_zf_min(self):
        text = self.zf_min.text().strip()
        if not text:
            return
        try:
            value = float(text)
            if value <= 0:
                QMessageBox.warning(self, "输入错误", "涨幅最小值必须大于0！")
                self.zf_min.clear()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "涨幅输入无效！")
            self.zf_min.clear()

    def validate_zf_max(self):
        text = self.zf_max.text().strip()
        if not text:
            return
        try:
            value = float(text)
            if value <= 0:
                QMessageBox.warning(self, "输入错误", "涨幅最大值必须大于0！")
                self.zf_max.clear()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "涨幅输入无效！")
            self.zf_max.clear()

    def validate_yfzzf_min(self):
        text = self.yfzzf_min.text().strip()
        if not text:
            return
        try:
            value = float(text)
            if value <= 0:
                QMessageBox.warning(self, "输入错误", "一分钟涨幅最小值必须大于0！")
                self.yfzzf_min.clear()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "一分钟涨幅输入无效！")
            self.yfzzf_min.clear()

    def validate_yfzzf_max(self):
        text = self.yfzzf_max.text().strip()
        if not text:
            return
        try:
            value = float(text)
            if value <= 0:
                QMessageBox.warning(self, "输入错误", "一分钟涨幅最大值必须大于0！")
                self.yfzzf_max.clear()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "一分钟涨幅输入无效！")
            self.yfzzf_max.clear()

    def validate_price_min(self):
        text = self.price_min.text().strip()
        if not text:
            return
        try:
            value = float(text)
            if value <= 0:
                QMessageBox.warning(self, "输入错误", "股价最小值必须大于0！")
                self.price_min.clear()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "股价输入无效！")
            self.price_min.clear()

    def validate_price_max(self):
        text = self.price_max.text().strip()
        if not text:
            return
        try:
            value = float(text)
            if value <= 0:
                QMessageBox.warning(self, "输入错误", "股价最大值必须大于0！")
                self.price_max.clear()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "股价输入无效！")
            self.price_max.clear()
    #更新提示框
    def load_tsk(self):
        self.load_cj_data()

    #接收打了几个板数据，更新控件
    def set_dbsm2_text(self, value):
        dbnum=int(self.first_limit_combo.currentText().strip())-int(value)
        self.dbsm2.setText(str(dbnum))  # 在主线程中更新UI

    def enable_price_inputs(self):
        """启用股价输入框"""
        self.price_min.setEnabled(True)
        self.price_max.setEnabled(True)
        self.price_min.setStyleSheet("background-color: white;")
        self.price_max.setStyleSheet("background-color: white;")

    def disable_price_inputs(self):
        """禁用股价输入框并清空内容"""
        self.price_min.clear()
        self.price_max.clear()
        self.price_min.setEnabled(False)
        self.price_max.setEnabled(False)
        self.price_min.setStyleSheet("background-color: #f0f0f0;")
        self.price_max.setStyleSheet("background-color: #f0f0f0;")

    def enable_kpzf_inputs(self):
        """启用换手率输入框"""
        self.kpzf_min.setEnabled(True)
        self.kpzf_max.setEnabled(True)
        self.kpzf_min.setStyleSheet("background-color: white;")
        self.kpzf_max.setStyleSheet("background-color: white;")

    def disable_kpzf_inputs(self):
        """禁用换手率输入框并清空内容"""
        self.kpzf_min.clear()
        self.kpzf_max.clear()
        self.kpzf_min.setEnabled(False)
        self.kpzf_max.setEnabled(False)
        self.kpzf_min.setStyleSheet("background-color: #f0f0f0;")
        self.kpzf_max.setStyleSheet("background-color: #f0f0f0;")

    def enable_hsl_inputs(self):
        """启用换手率输入框"""
        self.yfzzf_min.setEnabled(True)
        self.yfzzf_max.setEnabled(True)
        self.yfzzf_min.setStyleSheet("background-color: white;")
        self.yfzzf_max.setStyleSheet("background-color: white;")

    def disable_hsl_inputs(self):
        """禁用换手率输入框并清空内容"""
        self.yfzzf_min.clear()
        self.yfzzf_max.clear()
        self.yfzzf_min.setEnabled(False)
        self.yfzzf_max.setEnabled(False)
        self.yfzzf_min.setStyleSheet("background-color: #f0f0f0;")
        self.yfzzf_max.setStyleSheet("background-color: #f0f0f0;")

    def enable_zf_inputs(self):

        self.zf_min.setEnabled(True)
        self.zf_max.setEnabled(True)
        self.zf_min.setStyleSheet("background-color: white;")
        self.zf_max.setStyleSheet("background-color: white;")

    def disable_zf_inputs(self):
        self.zf_min.clear()
        self.zf_max.clear()
        self.zf_min.setEnabled(False)
        self.zf_max.setEnabled(False)
        self.zf_min.setStyleSheet("background-color: #f0f0f0;")
        self.zf_max.setStyleSheet("background-color: #f0f0f0;")

    #"""重写 showEvent 方法，在窗口显示后加载数据并验证连接"""
    def showEvent(self, event):

        super().showEvent(event)
        # 默认勾选“主板”和“首板”
        self.checkbox_main.setChecked(True)


        # 访问券商信息,消耗资源的加载全部改为线程处理，不会堵塞主界面
        load_username_account_thred = threading.Thread(target= self.load_username_account_data)
        load_username_account_thred.start()

        # 加载金额数据
        load_db1_data_thread = threading.Thread(target=self.load_db1_data())
        load_db1_data_thread.start()

        load_cj_data_thread = threading.Thread(target=self.load_cj_data())
        load_cj_data_thread.start()

        # 触发选择框变化事件进行连接验证
        if self.combo_box_qmt.count() > 0:
            self.combo_box_qmt.setCurrentIndex(0)
            # 使用多线程进行连接验证
            #threading.Thread(target=self.on_combo_box_changed).start()
        self.phsj_timer()

        # 更新提示框
        self.tsk.connect(self.load_tsk)  # 连接信号到槽
        #按钮互斥
        self.zf_switch.switched_on.connect(lambda: self.handle_switch_mutex(self.zf_switch))
        self.yfzzf_switch.switched_on.connect(lambda: self.handle_switch_mutex(self.yfzzf_switch))
        self.price_switch.switched_on.connect(lambda: self.handle_switch_mutex(self.price_switch))

    def handle_switch_mutex(self, activated_switch):
        """处理三个开关的互斥逻辑"""
        switches = {
            "zf": self.zf_switch,
            "yfzzf": self.yfzzf_switch,
            "price": self.price_switch
        }

        # 关闭其他开关
        for key in switches:
            if switches[key] != activated_switch:
                if switches[key].is_checked:
                    switches[key].is_checked = False
                    # 触发对应的关闭信号
                    if key == "zf":
                        self.disable_zf_inputs()
                    elif key == "yfzzf":
                        self.disable_hsl_inputs()
                    elif key == "price":
                        self.disable_price_inputs()
                    # 强制更新按钮状态
                    #switches[key].update_button_style()


    #加载盘后数据定时
    def phsj_timer(self):
        # 加载盘后数据
        hoo = ChinaHolidays()
        jy = hoo.is_china_stock_trading_time_d()
        if not jy:
            if self.win and hasattr(self.win, "_model"):
                row_count = self.win._model.rowCount()
                if row_count > 0:
                    self.update_no_trader_thread = threading.Thread(target=self.update_no_trader_data_thread, args=(row_count,))
                    self.update_no_trader_thread.start()




    #加载成交提示信息
    def load_cj_data(self):
        today = date.today()
        # 格式化日期为 2025-02-23 这种形式
        rq = today.strftime("%Y-%m-%d")
        czlx="tjd"
        action = "load_cj_data"
        deal = DeaiClientData()
        result = deal.load_cj_data(action, self.username,rq,czlx)
        if result:
            # 先清空 QListWidget 中的所有项
            self.q_list.clear()
            for item in result:
                gpmc = item["gpmc"]
                cj_nr_str = item["cj_nr"].replace("'", "\"")
                cj_nr = json.loads(cj_nr_str)

                gpdm=item["gpdm"]
                num = cj_nr["num"]
                price = cj_nr["price"]
                cj_zt=cj_nr["cj_zt"]
                date_time=cj_nr["date_time"]

                info_str=f"{date_time},买入{gpmc}({gpdm}),{num}股,{price},{cj_zt}"
                list_item = QListWidgetItem(info_str)
                # 设置字体颜色为蓝色
                list_item.setForeground(QBrush(QColor(0, 0, 255)))
                # 将 QListWidgetItem 添加到 QListWidget 中
                self.q_list.addItem(list_item)


    # 加载页面保存的数据
    def load_db1_data(self):
        action = "load_db1_data"
        dblx = "tjd"
        deal = DeaiClientData()
        result = deal.load_db1_data(action, self.username, dblx)
        if result:

            # 假设 result 是一个列表，取第一个元素
            item = result[0]
            # 发送信号到主线程
            self.db1_data_ready.emit(item)


    # 新增槽函数处理UI更新
    def handle_db1_data(self, item):
        # 在原有代码中找到设置开关状态的位置，添加：
        enabled_switches = 0
        if self.zf_switch.is_checked: enabled_switches += 1
        if self.yfzzf_switch.is_checked: enabled_switches += 1
        if self.price_switch.is_checked: enabled_switches += 1

        if enabled_switches > 1:
            QMessageBox.warning(self, "配置错误", "检测到多个条件开关同时开启，已自动修正为最后一个开启项")
            # 保留最后一个开启的开关，关闭其他
            last_switch = None
            if self.price_switch.is_checked: last_switch = self.price_switch
            if self.yfzzf_switch.is_checked: last_switch = self.yfzzf_switch
            if self.zf_switch.is_checked: last_switch = self.zf_switch

            if last_switch:
                self.handle_switch_mutex(last_switch)
        try:
            # 解析 cele 字段
            try:
                cele_data = json.loads(item.get('cele', '{}'))
            except json.JSONDecodeError as e:
                logger.error('tjd_ym:handle_db1_data:JSON 解析失败', exc_info=True)
                return
            # 板块复选框
            bk = cele_data.get('bk', [])
            self.checkbox_main.setChecked('主板' in bk)
            self.checkbox_gem.setChecked('创业板和科创板' in bk)
            self.checkbox_star.setChecked('北交所' in bk)

            # 全选复选框状态调整
            all_selected = len(bk) == 3 and '主板' in bk and '创业板和科创板' in bk and '北交所' in bk
            self.checkbox_all.setChecked(all_selected)
            self.checkbox_main.setEnabled(not all_selected)
            self.checkbox_gem.setEnabled(not all_selected)
            self.checkbox_star.setEnabled(not all_selected)

            # 每只股票买入金额输入框
            self.mzgpmre_input.setText(cele_data.get('mzgpmrje', ''))

            # 总资金输入框
            self.zzje_input.setText(cele_data.get('zzje', ''))

            # 涨停后炸板买入作废
            # if "ztzbfb" in cele_data:
            # self.ztzbfb.is_checked=True

            # 流通市值输入框
            if "zf_min" in cele_data:
                self.zf_switch.is_checked = True
                self.zf_min.setText(cele_data.get('zf_min', ''))
            if "zf_max" in cele_data:
                self.zf_switch.is_checked = True
                self.zf_max.setText(cele_data.get('zf_max', ''))

            # 流通市值输入框
            if "price_min" in cele_data:
                self.price_switch.is_checked = True
                self.price_min.setText(cele_data.get('price_min', ''))
            if "price_max" in cele_data:
                self.price_switch.is_checked = True
                self.price_max.setText(cele_data.get('price_max', ''))

            # 换手率
            if "yfzzf_min" in cele_data:
                self.yfzzf_switch.is_checked = True
                self.yfzzf_min.setText(cele_data.get('yfzzf_min', ''))
            if "yfzzf_max" in cele_data:
                self.yfzzf_switch.is_checked = True
                self.yfzzf_max.setText(cele_data.get('hsl_max', ''))

            # 最先符合条件的股票
            first_limit_value = cele_data.get('zxzt_total', '')
            self.first_limit_combo.setCurrentText(first_limit_value)

            # 买入设置
            buysz = cele_data.get('buysz', '')
            self.sell_position_combo.setCurrentText(buysz)

            # 处理买一封板资金输入框
            if 'buyfbzj' in cele_data:
                # 创建水平布局并添加输入框和标签
                if hasattr(self, 'capital_input'):
                    if self.capital_input.isWidgetType():
                        self.capital_input.setText(cele_data['buyfbzj'])

            # 处理卖一封单
            if 'myfd' in cele_data:
                # 创建水平布局并添加输入框和标签
                if hasattr(self, 'myfd_input'):
                    if self.myfd_input.isWidgetType():
                        self.myfd_input.setText(cele_data['myfd'])

            # 时间范围输入框
            start_time = cele_data.get('start_time_spinbox', 570)
            end_time = cele_data.get('end_time_spinbox', 900)
            self.start_time_spinbox.setValue(start_time)
            self.end_time_spinbox.setValue(end_time)

            # 换手率输入框
            self.yfzzf_min.setText(cele_data.get('yfzzf_min', ''))
            self.yfzzf_max.setText(cele_data.get('yfzzf_max', ''))

            # 将数据加载到list中
            self.win._model.list_row(item.get('list', '[]'))


        except Exception as e:
            logger.error('handle_db1_data:UI更新失败', exc_info=True)
            QMessageBox.critical(self, "错误", "数据加载失败，请重试！")


    def format_input(self, text):
        # 去除已有逗号
        clean_text = re.sub(r',', '', text)
        try:
            num = float(clean_text)
            # 添加千分位分隔符
            formatted_text = "{:,}".format(num)
            # 保存当前光标位置
            cursor_pos = self.mzgpmre_input.cursorPosition()
            # 断开信号连接避免循环
            self.mzgpmre_input.textChanged.disconnect(self.format_input)
            self.mzgpmre_input.setText(formatted_text)
            # 重新连接信号
            self.mzgpmre_input.textChanged.connect(self.format_input)
            # 调整光标位置
            new_cursor_pos = len(formatted_text) - (len(clean_text) - cursor_pos)
            self.mzgpmre_input.setCursorPosition(new_cursor_pos)
        except ValueError:
            pass

    #调用券商地址信息
    def load_username_account_data(self):
        deal = DeaiClientData()
        action = "load_username_account_data"
        username = self.username
        acc_data = deal.load_username_account_data(action, username)

        # 分离mr_zt为'1'的账户和其他账户
        mr1_accounts = []
        other_accounts = []
        if acc_data:
            for acc in acc_data:
                if str(acc['mr_zt']) == '1':
                    mr1_accounts.append(acc)
                else:
                    other_accounts.append(acc)

            # 生成排序后的xz_data，mr_zt为1的在前
            xz_data = []
            for acc in mr1_accounts + other_accounts:
                item_str = f"{acc['dz']}（{acc['account']}）"
                xz_data.append(item_str)
            # 通过信号发送数据到主线程
            self.combo_data_ready.emit(xz_data)  #对接  update_combo_box 方法

    # 新增槽函数处理UI更新


    def update_combo_box(self, xz_data):
        """更新组合框的槽函数"""
        self.combo_box_qmt.clear()
        self.combo_box_qmt.addItems(xz_data)
        self.combo_box_qmt.setStyleSheet("""
                      QComboBox {
                          background-color: white; 
                          font-size: 11px;
                      }
                      QComboBox QAbstractItemView {
                          font-size: 11px;
                      }
                  """)

        if xz_data:
            self.combo_box_qmt.setCurrentIndex(0)


    # 上午半小时按钮
    def on_swbxs_button_clicked(self):
        start_time = 9 * 60 + 30  # 9:30
        end_time = 10 * 60  # 10:30
        # 获取当前时间
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        ho=ChinaHolidays()
        jy_start_time=9 * 60 + 30
        jy_end_time = 15 * 60 + 30
        #在交易日交易时间内才能设置
        if not ho.is_china_stock_trading_time() and jy_start_time<=current_minutes<=jy_end_time:
            # 检查当前时间是否在范围内
            if current_minutes < start_time or current_minutes > end_time:
                QMessageBox.warning(self, "时间超出范围", "当前时间已经超出所给的时间，请重新设置。")
                return


        # 设置开始时间为 9:30（9 * 60 + 30 = 570 分钟）
        self.start_time_spinbox.setValue(start_time)

        # 设置结束时间为 10:00（10 * 60 + 0 = 600 分钟）
        self.end_time_spinbox.setValue(end_time)

    # 上午一小时按钮
    def on_swyxs_button_clicked(self):
        """
        点击“上午一小时”按钮时触发的事件
        """
        start_time = 9 * 60 + 30  # 9:30
        end_time = 10 * 60 + 30  # 10:30

        # 获取当前时间
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        ho = ChinaHolidays()
        jy_start_time = 9 * 60 + 30
        jy_end_time = 15 * 60 + 30
        # 在交易日交易时间内才能设置
        if not ho.is_china_stock_trading_time() and jy_start_time <= current_minutes <= jy_end_time:
            # 检查当前时间是否在范围内
            if current_minutes < start_time or current_minutes > end_time:
                QMessageBox.warning(self, "时间超出范围", "当前时间已经超出所给的时间，请重新设置。")
                return

        # 设置开始时间为 9:30（9 * 60 + 30 = 570 分钟）
        self.start_time_spinbox.setValue(start_time)

        # 设置结束时间为 10:30（10 * 60 + 30 = 630 分钟）
        self.end_time_spinbox.setValue(end_time)

    # 上午
    def on_sw_button_clicked(self):
        """
        点击“上午半小时”按钮时触发的事件
        """
        # 设置开始时间为 9:30（9 * 60 + 30 = 570 分钟）
        start_time =9 * 60 + 30 # 9:30
        end_time = 11 * 60 + 30  # 10:30

        # 获取当前时间
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        ho = ChinaHolidays()
        jy_start_time = 9 * 60 + 30
        jy_end_time = 15 * 60 + 30
        # 在交易日交易时间内才能设置
        if not ho.is_china_stock_trading_time() and jy_start_time <= current_minutes <= jy_end_time:
            # 检查当前时间是否在范围内
            if current_minutes < start_time or current_minutes > end_time:
                QMessageBox.warning(self, "时间超出范围", "当前时间已经超出所给的时间，请重新设置。")
                return

        self.start_time_spinbox.setValue(start_time)

        # 设置结束时间为 10:00（10 * 60 + 0 = 600 分钟）
        self.end_time_spinbox.setValue(end_time)


    # 下午
    def on_xw_button_clicked(self):
        # 临时断开信号连接
        start_time =13 * 60  # 9:30
        end_time = 15 * 60  # 10:30

        # 获取当前时间
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        ho = ChinaHolidays()
        jy_start_time = 9 * 60 + 30
        jy_end_time = 15 * 60 + 30
        # 在交易日交易时间内才能设置


        # 设置开始时间为 13:00（13 * 60 = 780 分钟）
        self.start_time_spinbox.setValue(start_time)
        # 设置结束时间为 15:00（15 * 60 = 900 分钟）
        self.end_time_spinbox.setValue(end_time)


    #全天
    def on_qt_button_clicked(self):
        """
        点击“上午半小时”按钮时触发的事件
        """

        # 设置开始时间为 9:30（9 * 60 + 30 = 570 分钟）
        start_time = 9 * 60 + 30  # 9:30
        end_time =15 * 60  # 10:30

        # 获取当前时间
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        ho = ChinaHolidays()
        jy_start_time = 9 * 60 + 30
        jy_end_time = 15 * 60 + 30
        # 在交易日交易时间内才能设置
        if not ho.is_china_stock_trading_time() and jy_start_time <= current_minutes <= jy_end_time:
            # 检查当前时间是否在范围内
            if current_minutes < start_time or current_minutes > end_time:
                QMessageBox.warning(self, "时间超出范围", "当前时间已经超出所给的时间，请重新设置。")
                return
        # 设置开始时间为 9:30（9 * 60 + 30 = 570 分钟）
        self.start_time_spinbox.setValue(start_time)
        # 设置结束时间为 10:00（10 * 60 + 0 = 600 分钟）
        self.end_time_spinbox.setValue(end_time)

    # 测试连接
    def on_combo_box_changed(self):
        self.test_button.setStyleSheet("""
                QPushButton {
                    background-color: yellow;
                    border: none;
                    color: white;
                    padding: 5px 10px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 14px;
                    border-radius: 5px;
                }
                QPushButton:pressed {
                    background-color: #FFCCCB;
                }
            """)
        self.button_timer.start(500)  # 开始定时器，每500毫秒切换一次颜色

        on_combo_box_changed_thread = threading.Thread(target=self.on_combo_box_changed_thread)
        on_combo_box_changed_thread.start()

    # 测试连接线程
    def on_combo_box_changed_thread(self):
        """
        当 combo_box_qmt 的值发生变化时触发
        :param text: 选择的文本，格式为 "地址（账号）"
        """
        text = self.combo_box_qmt.currentText()
        self.trader =None
        if text:


            address, account = self.parse_account_text(text)

            # 将地址和账号传递给 qmt_trader
            trader = qmt_trader(address, account, self.username)  # 假设 qmt_trader 接受地址和账号作为参数

            # 创建信号对象
            signal = ConnectionResultSignal()
            signal.result_signal.connect(self.handle_connection_result)


            def check_connection():
                try:
                    # 检查连接状态
                    result = trader.ch_connection_status()
                    #把获取到的交易对象保存起来
                    if result["result"] == "ok":
                        qm=save_qmt()
                        rel=qm.yz_tader(account)
                        if rel:
                            self.trader=qm.get_tader(account)
                        else:
                          save_qmt().save_tader(account, trader)
                          self.trader=trader
                        #得到了对象
                        #print(f"acc:{save_qmt().get_tader(account)}")
                except Exception as e:
                    logger.error('tjd_ym:check_connection:连接验证时出现异常', exc_info=True)
                    result = {"result": "error", "message": f"连接验证时出现异常: {str(e)}"}
                # 发送信号，将结果传递给主线程
                signal.result_signal.emit(result)

            # 使用多线程进行连接验证
            threading.Thread(target=check_connection).start()

        else:
            self.button_timer.stop()  # 停止定时器
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ths_image_dir = os.path.join(script_dir)
            checkmark_icon = QIcon(f"{ths_image_dir}/image/ch.png")
            self.test_button.setIcon(checkmark_icon)
            self.test_button.setStyleSheet("""
                           QPushButton {
                               background-color: black;
                               border: none;
                               color: white;
                               padding: 5px 10px;
                               text-align: center;
                               text-decoration: none;
                               font-size: 14px;
                               border-radius: 5px;
                           }
                           QPushButton::icon {
                               width: 25px;  /* 调整图片宽度 */
                               height: 25px; /* 调整图片高度 */
                           }
                       """)
            return


    def toggle_button_color(self):
        current_style = self.test_button.styleSheet()
        if "background-color: yellow" in current_style:
            new_style = current_style.replace("background-color: yellow", "background-color: gray")
        else:
            new_style = current_style.replace("background-color: gray", "background-color: yellow")
        self.test_button.setStyleSheet(new_style)

    def handle_connection_result(self, result):
        self.button_timer.stop()  # 停止定时器
        if result["result"] == "ok":
            self.qmt_trader = self.trader
            self.trader = None
            self.ceshi_zt = 1

            # 获取基础路径
            base_path = path().get_base_path()
            # 使用os.path.join构建日志目录路径
            log_dir = os.path.join(base_path, 'photo')
            # 构建完整日志文件路径
            log_file = os.path.join(log_dir, 'dh.png')
            checkmark_icon = QIcon(log_file)
            self.test_button.setIcon(checkmark_icon)
            self.test_button.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    border: none;
                    color: white;
                    padding: 5px 10px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 14px;
                    border-radius: 5px;
                }
                QPushButton::icon {
                    width: 25px;  /* 调整图片宽度 */
                    height: 25px; /* 调整图片高度 */
                }
            """)
        else:
            self.ceshi_zt = 0
            # 获取基础路径
            base_path = path().get_base_path()
            # 使用os.path.join构建日志目录路径
            log_dir = os.path.join(base_path, 'photo')
            # 构建完整日志文件路径
            log_file = os.path.join(log_dir, 'ch.png')
            checkmark_icon = QIcon(log_file)
            self.test_button.setIcon(checkmark_icon)
            self.test_button.setStyleSheet("""
                QPushButton {
                    background-color: black;
                    border: none;
                    color: white;
                    padding: 5px 10px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 14px;
                    border-radius: 5px;
                }
                QPushButton::icon {
                    width: 25px;  /* 调整图片宽度 */
                    height: 25px; /* 调整图片高度 */
                }
            """)
            QMessageBox.warning(self, "连接状态", result["message"])

    #时间输入框验证
    def on_start_time_changed(self, value):
        # 定义允许的时间段：9:25-11:00 (565-660) 和 13:00-15:00 (780-900)
        if 690 < value < 780:  # 11:30-13:00区间自动调整为11:00
            new_value = 780
        elif value < 565:  # 早于9:25调整为9:25
            new_value = 565
        elif value > 900:  # 晚于15:00调整为15:00
            new_value = 900
        else:
            new_value = value

        # 如果值被调整，需要更新控件
        if new_value != value:
            self.start_time_spinbox.valueChanged.disconnect(self.on_start_time_changed)
            self.start_time_spinbox.setValue(new_value)
            self.start_time_spinbox.valueChanged.connect(self.on_start_time_changed)
            return  # 调整后直接返回，避免重复处理

        # 原有时间范围校验逻辑f
        if not hasattr(self, 'end_time_spinbox') or self.end_time_spinbox is None:
            return

        end_time_value = self.end_time_spinbox.value()
        if new_value >= end_time_value:
            new_start_value = end_time_value - 1
            if new_start_value < 565:  # 不能小于最小开始时间
                new_start_value = 565
            self.start_time_spinbox.valueChanged.disconnect(self.on_start_time_changed)
            self.start_time_spinbox.setValue(new_start_value)
            self.start_time_spinbox.valueChanged.connect(self.on_start_time_changed)

    def on_end_time_changed(self, value):
        # 定义允许的时间段：9:40-11:30 (580-690) 和 13:00-15:00 (780-900)
        if 690 < value < 780:  # 11:30-13:00区间自动调整为13:00
            new_value = 780
        elif value < 580:  # 早于9:40调整为9:40
            new_value = 580
        elif value > 900:  # 晚于15:00调整为15:00
            new_value = 900
        else:
            new_value = value

        # 如果值被调整，需要更新控件
        if new_value != value:
            self.end_time_spinbox.valueChanged.disconnect(self.on_end_time_changed)
            self.end_time_spinbox.setValue(new_value)
            self.end_time_spinbox.valueChanged.connect(self.on_end_time_changed)
            return  # 调整后直接返回，避免重复处理

        # 原有时间范围校验逻辑
        if not hasattr(self, 'start_time_spinbox') or self.start_time_spinbox is None:
            return

        start_time_value = self.start_time_spinbox.value()
        if new_value <= start_time_value:
            new_end_value = start_time_value + 1
            if new_end_value > 900:  # 不能超过最大结束时间
                new_end_value = 900
            self.end_time_spinbox.valueChanged.disconnect(self.on_end_time_changed)
            self.end_time_spinbox.setValue(new_end_value)
            self.end_time_spinbox.valueChanged.connect(self.on_end_time_changed)






    #刷新资金余额
    def on_refresh_button_clicked(self):
        """
        刷新资金余额按钮的点击事件
        """
        if self.qmt_trader is None:
            # 如果 qmt_trader 为 None，提示用户登录并测试连接
            QMessageBox.warning(self, "提示", "连接失败：请登录券商QMT软件！")
        else:
            # 如果 qmt_trader 不为 None，刷新资金余额
            try:
                # 调用 qmt_trader 获取资金余额
                balance = self.qmt_trader.queryye() # 假设 qmt_trader 有一个 get_balance 方法
                self.balance_label.setText(f"{balance:.2f}")  # 更新资金余额显示
            except Exception as e:
                # 如果获取余额失败，显示错误信息
                logger.error('tjd_ym:on_refresh_button_clicked:连接失败', exc_info=True)
                QMessageBox.warning(self, "错误", f"连接失败：请重新登录软件！")

    def parse_account_text(self, text):
        """
        解析账户文本，提取地址和账号
        :param text: 格式为 "地址（账号）"
        :return: address, account
        """
        parts = text.split("（")
        if len(parts) != 2:
            return "", ""
        address = parts[0].strip()  # 获取地址
        account = parts[1].replace("）", "").strip()  # 获取账号
        return address, account


    def update_codes_list(self):
        holiday=ChinaHolidays()
        #如果是在交易日的11：30至13：00
        m=1
        if m:
            if  holiday.is_between_1130_and_1300_on_trading_day():
                if self.win and hasattr(self.win, "_model"):
                    row_count = self.win._model.rowCount()
                    if row_count > 0:
                        # 中午时间点
                        jy_thread = threading.Thread(target=self._update_11_13_thread, args=(row_count,))
                        jy_thread.start()
                        m=0

        if not holiday.is_china_stock_trading_time_d():
            return

        if self.win and hasattr(self.win, "_model"):
            row_count = self.win._model.rowCount()
            if row_count > 0:
                #if self.update_thread and self.update_thread.is_alive():
                    #print("上一次更新线程还在运行，跳过本次更新")
                    #return
                #在交易时间访问实时数据

                    #实时交易数据
                #self.update_thread = threading.Thread()
                #self.update_thread.start()
                self.thread_pool.submit(self._update_codes_list_thread,row_count)


                #非交易时间显示的数据
            else:
                print("表格中没有数据，不更新代码列表")
        else:
            print("表格控件未初始化，无法更新代码列表")

        #交易时间加载的数据
    def _update_codes_list_thread(self, row_count):
        try:
            self.codes_list = []
            for row in range(row_count):
                code_item = self.win._model.item(row, 2)
                if code_item is not None:
                    code = code_item.text()
                    self.codes_list.append(code)

            all_data = []
            for i in range(0, len(self.codes_list), 80):
                sub_codes_list = self.codes_list[i:i + 80]
                zh_lx=Account.zh_lx
                action = 'get_tick_datas'
                deal = DeaiClientData()
                data = deal.get_tick_datas(action, sub_codes_list,zh_lx)

                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError as e:
                        logger.error('tjd_ym:_update_codes_list_thread:JSON 解析失败', exc_info=True)
                        continue


                if data is not None:
                    all_data.extend(data)

            data = all_data
            if data:
                for item in data:
                    code = item['code']
                    price = float(item['close'])
                    vol = int(item['vol'])
                    # 发射信号到主线程
                    self.stock_data_updated.emit({
                        'code': code,
                        'price': price,
                        'vol': vol
                    })
               # print("更新代码列表:", self.codes_list)
            else:
                print("未获取到实时数据")
        except Exception as e:
            logger.error('tjd_ym:_update_codes_list_thread:更新代码列表时出现异常', exc_info=True)
        finally:
            self.update_thread = None  # 线程执行完毕，重置线程对象

    def handle_stock_data_update(self, data):
        code = data['code']
        price = data['price']
        vol = data['vol']
        for row in range(self.win._model.rowCount()):
            code_item = self.win._model.item(row, 2)
            if code_item is not None and code_item.text() == code:
                price_item = self.win._model.item(row, 3)
                if price_item is not None:
                    price_item.setText(str(price))

                    close_price_item = self.win._model.item(row, 10)
                    vol_item = self.win._model.item(row, 9)
                    if close_price_item is not None:
                        close_price = float(close_price_item.text())
                        ltgb_vol = int(float(vol_item.text()))
                        if close_price != 0:
                            change_percent = (price - close_price) / close_price * 100
                            change_text = f"{change_percent:.2f}%"
                            change_item = self.win._model.item(row, 4)
                            change_item.setText(change_text)

                            vol_percent = (vol / ltgb_vol) * 10000
                            vol_text = f"{vol_percent:.2f}%"
                            vol_item = self.win._model.item(row, 5)
                            vol_item.setText(vol_text)

                            if change_percent > 0:
                                change_item.setForeground(QBrush(Qt.red))
                            elif change_percent < 0:
                                change_item.setForeground(QBrush(QColor(0, 100, 0)))
                            else:
                                change_item.setForeground(QBrush(Qt.black))
                    break


    # 交易时间加载的数据
    def _update_11_13_thread(self, row_count):
        try:
            self.codes_list = []
            for row in range(row_count):
                code_item = self.win._model.item(row, 2)
                if code_item is not None:
                    code = code_item.text()
                    self.codes_list.append(code)

            all_data = []
            for i in range(0, len(self.codes_list), 80):
                sub_codes_list = self.codes_list[i:i + 80]
                action = 'get_rencent_datas'
                deal = DeaiClientData()
                data = deal.get_rencent_datas(action, sub_codes_list)

                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError as e:
                        logger.error('tjd_ym:_update_codes_list_thread:JSON 解析失败', exc_info=True)
                        continue
                if data is not None:
                    all_data.extend(data)

            data = all_data

            if data:
                for item in data:
                    code = item['code']
                    price = float(item['close'])
                    vol = int(float(item['vol']))
                    for row in range(row_count):
                        code_item = self.win._model.item(row, 2)
                        if code_item is not None and code_item.text() == code:
                            price_item = self.win._model.item(row, 3)
                            if price_item is not None:
                                price_item.setText(str(price))

                                close_price_item = self.win._model.item(row, 10)
                                vol_item = self.win._model.item(row, 9)
                                if close_price_item is not None:
                                    close_price = float(close_price_item.text())
                                    close_vol = float(vol_item.text())
                                    if close_price != 0:
                                        change_percent = (price - close_price) / close_price * 100
                                        change_text = f"{change_percent:.2f}%"
                                        change_item = self.win._model.item(row, 4)
                                        change_item.setText(change_text)

                                        vol_percent = (vol / close_vol) * 100
                                        vol_text = f"{vol_percent:.2f}%"
                                        vol_item = self.win._model.item(row, 5)
                                        vol_item.setText(vol_text)

                                        if change_percent > 0:
                                            change_item.setForeground(QBrush(Qt.red))
                                        elif change_percent < 0:
                                            change_item.setForeground(QBrush(QColor(0, 100, 0)))
                                        else:
                                            change_item.setForeground(QBrush(Qt.black))
                                break
            # print("更新代码列表:", self.codes_list)
            else:
                print("未获取到实时数据")
        except Exception as e:
            logger.error('tjd_ym:_update_11_13_thread:更新代码列表时出现异常', exc_info=True)
        finally:
            self.update_thread = None  # 线程执行完毕，重置线程对象

    #非交易时间加载的数据
    def update_no_trader_data_thread(self, row_count):
        try:
            self.codes_list = []
            for row in range(row_count):
                code_item = self.win._model.item(row, 2)
                if code_item is not None:
                    code = code_item.text()
                    self.codes_list.append(code)

            all_data = []
            action = 'get_gp_close_datas'
            deal = DeaiClientData()
            data = deal.get_gp_close_datas(action, self.codes_list)

            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error('tjd_ym:_update_codes_list_thread:JSON 解析失败', exc_info=True)

            if data is not None:
                all_data.extend(data)

            data = all_data

            if data:
                for item in data:
                    code = item['gpdm']
                    price = float(item['xj'])
                    vol = int(float(item['vol']))
                    ltgbnum = int(float(item['ltgbnum']))

                    close_price = float(item['close_pre_day_price'])
                    for row in range(row_count):
                        code_item = self.win._model.item(row, 2)
                        if code_item is not None and code_item.text() == code:
                            price_item = self.win._model.item(row, 3)
                            if price_item is not None:
                                price_item.setText(str(price))

                                vol_item = self.win._model.item(row, 5)
                                if close_price is not None:
                                    if close_price != 0:
                                        change_percent = (price - close_price) / close_price*100
                                        change_text = f"{change_percent:.2f}%"
                                        change_item = self.win._model.item(row, 4)
                                        change_item.setText(change_text)

                                        vol_percent = (vol / ltgbnum) * 100
                                        vol_text = f"{vol_percent:.2f}%"
                                        vol_item = self.win._model.item(row, 5)
                                        vol_item.setText(vol_text)

                                        if change_percent > 0:
                                            change_item.setForeground(QBrush(Qt.red))
                                        elif change_percent < 0:
                                            change_item.setForeground(QBrush(QColor(0, 100, 0)))
                                        else:
                                            change_item.setForeground(QBrush(Qt.black))
                                break
               # print("更新代码列表:", self.codes_list)
            else:
                print("未获取到实时数据")
        except Exception as e:
            logger.error('tjd_ym:update_no_trader_data_thread:更新代码列表时出现异常', exc_info=True)
        finally:
            self.update_thread = None  # 线程执行完毕，重置线程对象



    def closeEvent(self, event):
        """重写 closeEvent 方法，在窗口关闭时停止 QTimer"""
        #self.timer.stop()  # 停止 QTimer
        event.accept()  # 接受关闭事件，关闭窗口


    def create_top_page(self):
        """创建顶部页面，高度固定为70"""
        top_page = QWidget()
        top_page.setFixedHeight(120)  # 固定高度为70
        top_page.setStyleSheet("background-color: #e6f0fc;font-size: 13px;")  # 设置背景颜色

        # 创建顶部布局（横向排列）
        top_layout = QHBoxLayout()
        top_layout.setSpacing(0)  # 设置布局的间距为 0
        top_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 0

        # 左边布局（宽100，高70，两个按钮上下放置）
        left_layout = QVBoxLayout()
        left_layout.setSpacing(0)  # 设置按钮之间的间距为 5 像素
        left_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 5 像素

        # 添加两个按钮

        #打板按钮
        self.switch_button = SwitchButton()
        # 连接信号和槽函数
        self.switch_button.switched_on.connect(self.on_switch_on)
        self.switch_button.switched_off.connect(self.on_switch_off)

        self.save_button = QPushButton("保存数据")
        self.save_button.setStyleSheet(" font-size: 15px")
        self.save_button.setFixedHeight(30)
        self.save_button.clicked.connect(self.save_button_clicked)


        #self.switch_button2 = BcSwitchButton()
        #button2.switched_on.connect(self.on_save_button_clicked)  # 按钮点击事件
        #self.switch_button2.switched_on.connect(self.on_switch_on)
        #self.switch_button2.switched_off.connect(self.on_switch_off)
        left_layout.addWidget(self.switch_button)
        left_layout.addWidget(self.save_button)
        #left_layout.addWidget( self.switch_button2)
        #父组件控制子组件的间距
        spacer = QSpacerItem(50, 5, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # 左边布局容器
        left_widget = QWidget()
        left_widget.setFixedWidth(110)  # 设置左边布局宽度为 100
        left_widget.setLayout(left_layout)

        # 右边布局
        right_layout = QVBoxLayout()
        right_layout.setSpacing(0)  # 设置组件之间的间距为 5 像素
        right_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 5 像素

        #第0行
        account_layout=QHBoxLayout()
        account_layout.setSpacing(20)
        account_layout.setContentsMargins(20, 0, 0, 0)
        account_layout.setAlignment(Qt.AlignLeft)  # 设置左对齐
        #选择框和测试按钮
        qmt_widget = QWidget()

        qmt_widget.setFixedWidth(420)
        qmt_widget.setContentsMargins(0,0,0,0)
        qmt_layout = QHBoxLayout(qmt_widget)
        qmt_layout.setContentsMargins(0, 0, 0, 0)
        # 添加选择框（QComboBox）
        self.combo_box_qmt = QComboBox()
        self.combo_box_qmt.setPlaceholderText("请运行QMT或者在交易连接设置中配置")  # 设置占位符文本
        self.combo_box_qmt.setFixedWidth(320)  # 设置选择框宽度
        self.combo_box_qmt.setFixedHeight(25)
        self.combo_box_qmt.setStyleSheet("background-color: white; font-size: 11px;")  # 设置样式
        self.combo_box_qmt.currentTextChanged.connect(self.on_combo_box_changed)  # 绑定选择框变化事件
        qmt_layout.addWidget(self.combo_box_qmt)

        # 添加测试连接按钮
        self.test_button = QPushButton("连接券商")
        self.test_button.setFixedHeight(25)
        self.test_button.setFixedWidth(100)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                border: none;
                color: white;
                padding: 5px 10px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                border-radius: 5px;
            }
           
            QPushButton:pressed {
                background-color: #FFCCCB;
            }
        """)
        self.test_button.clicked.connect(self.on_combo_box_changed)  # 绑定按钮点击事件
        qmt_layout.addWidget(self.test_button)
        account_layout.addWidget(qmt_widget)

        # 添加刷新资金余额按钮
        self.sxzj_widget = QWidget()
        self.sxzj_widget.setFixedWidth(230)
        self.sxzj_layout = QHBoxLayout(self.sxzj_widget)
        refresh_button = QPushButton("刷新资金余额：")
        refresh_button.clicked.connect(self.on_refresh_button_clicked)
        refresh_button.setFixedWidth(90)
        self.sxzj_layout.addWidget(refresh_button)
        # 添加资金余额 QLabel
        self.balance_label = QLabel("0.00")
        self.balance_label.setStyleSheet("background-color: gold;")  # 设置背景色为金色
        self.sxzj_layout.addWidget(self.balance_label)
        # 将第一行添加到右边布局
        account_layout.addWidget(self.sxzj_widget)
        # 刷新资金余额结束

        # 总资金
        self.zzje_widget = QWidget()
        self.zzje_widget.setFixedWidth(230)
        self.zzje_widget.setContentsMargins(0, 0, 0, 0)
        zzje_layout = QHBoxLayout(self.zzje_widget)
        zzje_layout.setContentsMargins(10, 0, 0, 0)
        self.zzje_label1 = QLabel("买入总金额不超过")
        self.zzje_input = moneySeparatedLineEdit()
        self.zzje_input.setValidator(QDoubleValidator(0, 999999999, 2, self))  # 限制只能输入数字
        self.zzje_input.setStyleSheet("background-color: gold;")  # 设置背景色为金色
        self.zzje_input.setFixedWidth(80)  # 设置输入框宽度
        self.zzje_input.setPlaceholderText("")  # 设置占位符文本
        self.zzje_input.setValidator(QDoubleValidator())  # 限制只能输入数字
        self.zzje_y_label = QLabel("元")
        zzje_layout.addWidget(self.zzje_label1)
        zzje_layout.addWidget(self.zzje_input)
        zzje_layout.addWidget(self.zzje_y_label)
        account_layout.addWidget(self.zzje_widget)
        # 总资金结束


        right_layout.addLayout(account_layout)



        # 第一行：四个 QCheckBox、一个 QComboBox、一个按钮和一个 QLabel
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(0)  # 设置组件之间的间距为 10 像素
        first_row_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 5 像素
        first_row_layout.setAlignment(Qt.AlignLeft)  # 设置左对齐
        # 添加主板开始
        bk_widget = QWidget()
        bk_layout = QHBoxLayout(bk_widget)
        bk_widget.setFixedWidth(300)
        self.checkbox_all = QCheckBox("全选：")
        self.checkbox_all.setFixedWidth(50)
        self.checkbox_all.stateChanged.connect(self.on_checkbox_all_changed)
        #self.checkbox_all =LittleSwitchButton()
        self.checkbox_main = QCheckBox("主板")
        self.checkbox_gem = QCheckBox("创业板和科创板")
        self.checkbox_star = QCheckBox("北交所")
        bk_layout.addWidget(self.checkbox_all)
        bk_layout.addWidget(self.checkbox_main)
        bk_layout.addWidget(self.checkbox_gem)
        bk_layout.addWidget(self.checkbox_star)
        first_row_layout.addWidget(bk_widget)
        # 添加主板结束


        # 买入最先符合条件的前 N 个股
        first_limit_widget = QWidget()
        first_limit_widget.setFixedWidth(230)  # 设置 QWidget 的宽度为 200 像素
        first_limit_widget.setContentsMargins(10, 0, 0, 0)
        first_limit_layout = QHBoxLayout(first_limit_widget)
        first_limit_layout.setSpacing(0)  # 设置组件之间的间距为 0 像素
        first_limit_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 0
        # 标签
        first_limit_label = QLabel("买入最先符合条件的前")
        first_limit_layout.addWidget(first_limit_label)
        # 选择框
        self.first_limit_combo = QComboBox()
        self.first_limit_combo.setStyleSheet("background-color: white;")
        self.first_limit_combo.addItems([str(i) for i in range(1, 21)])  # 添加选项 1 到 8
        self.first_limit_combo.setCurrentText("1")  # 设置默认值
        first_limit_layout.addWidget(self.first_limit_combo)
        # 标签
        first_limit_layout.addWidget(QLabel("个股票"))
        # 将打最先涨停布局添加到主布局中
        first_row_layout.addWidget(first_limit_widget)
        # 买入最先符合条件的前 N 个股




        #每只股票买入额度
        self.mzgpmre_widget = QWidget()
        self.mzgpmre_widget.setFixedWidth(280)
        mzgpmre_layout = QHBoxLayout(self.mzgpmre_widget)
        self.mzgpmre_label = QLabel("每只股票买入金额不超过")
        self.mzgpmre_input = moneySeparatedLineEdit()
        self.mzgpmre_input.setValidator(QDoubleValidator(0, 999999999, 2, self))  # 限制只能输入数字

        self.mzgpmre_input.setStyleSheet("background-color: gold;")
        self.mzgpmre_input.setFixedWidth(80)  # 设置输入框宽度
        self.mzgpmre_input.setPlaceholderText("")  # 设置占位符文本
        self.mzgpmre_input.setValidator(QDoubleValidator())  # 限制只能输入数字
        self.mzgpmre_y_label = QLabel("元")
        mzgpmre_layout.addWidget(self.mzgpmre_label)
        mzgpmre_layout.addWidget(self.mzgpmre_input)
        mzgpmre_layout.addWidget(self.mzgpmre_input)
        mzgpmre_layout.addWidget(self.mzgpmre_y_label)
        first_row_layout.addWidget(self.mzgpmre_widget)
        # 每只股票买入额度结束

        right_layout.addLayout(first_row_layout)

        # 第二行：三个 QCheckBox
        second_row_widget = QWidget()
        second_row_widget.setFixedWidth(920)
        second_row_layout = QHBoxLayout()
        second_row_widget.setLayout(second_row_layout)
        second_row_layout.setSpacing(0)  # 设置组件之间的间距为 10 像素
        second_row_layout.setAlignment(Qt.AlignRight)
        second_row_layout.setContentsMargins(0, 0, 0, 0)

        # 高速行情还是普通行情
        hq_widget = QWidget()
        hq_widget.setFixedWidth(120)
        hq_layout = QHBoxLayout(hq_widget)

        if Account.zh_lx:
            if Account.zh_lx == "0.9s":
                hq_label = QLabel("高速行情低档")
                hq_label.setStyleSheet("font-size: 14px; color: red;")
            if Account.zh_lx == "0.6s":
                hq_label = QLabel("高速行情中档")
                hq_label.setStyleSheet("font-size: 14px; color: red;")
            elif Account.zh_lx == "3s":
                hq_label = QLabel("普通行情")
                hq_label.setStyleSheet("font-size: 14px; color: #4169E1;")
            elif Account.zh_lx == "0.3s":
                hq_label = QLabel("高速行情最高档")
                hq_label.setStyleSheet("font-size: 14px; color: red;")


            hq_layout.addWidget(hq_label)
        second_row_layout.addWidget(hq_widget)
        # 高速行情还是普通行情

        # 赋值添加说明已经打了几个板
        dbsm_widget = QWidget()
        dbsm_widget.setFixedWidth(110)
        dbsm_layout = QHBoxLayout(dbsm_widget)
        self.dbsm1 = QLabel("已买")
        self.dbsm2 = QLabel("0")
        self.dbsm3 = QLabel("个股票")
        self.dbsm1.setStyleSheet("font-size: 14px; color: red;")
        self.dbsm2.setStyleSheet("font-size: 14px; color: red;")
        self.dbsm3.setStyleSheet("font-size: 14px; color: red;")
        dbsm_layout.addWidget(self.dbsm1)
        dbsm_layout.addWidget(self.dbsm2)
        dbsm_layout.addWidget(self.dbsm3)
        second_row_layout.addWidget(dbsm_widget)
        # 赋值添加说明已经打了几个板

        # 添加买入设置说明标签
        mcsz_wigth = QWidget()
        mcsz_wigth.setFixedWidth(260)
        mcsz_wigth.setContentsMargins(50, 0, 0, 0)
        mcsz_layout = QHBoxLayout(mcsz_wigth)

        sell_label = QLabel("买入设置:")
        sell_label.setFixedWidth(120)  # 设置标签宽度
        sell_label.setFixedHeight(25)
        sell_label.setStyleSheet("font-size: 14px;")  # 设置样式
        mcsz_layout.addWidget(sell_label)

        # 添加卖出位置下拉框
        self.sell_position_combo = QComboBox()
        self.sell_position_combo.addItems(["卖二", "卖三", "卖四", "卖五", "1%", "1.8%"])
        self.sell_position_combo.setFixedWidth(100)  # 设置选择框宽度
        self.sell_position_combo.setFixedHeight(25)
        self.sell_position_combo.setStyleSheet("background-color: white; font-size: 14px;")  # 设置样式
        # 将下拉框的 currentIndexChanged 信号连接到槽函数
        mcsz_layout.addWidget(self.sell_position_combo)
        second_row_layout.addWidget(mcsz_wigth)




        self.yxsj_widget = QWidget()
        #self.yxsj_widget.setStyleSheet("border: 1px solid black; border-radius: 5px; padding: 5px;")
        self.yxsj_widget.setFixedWidth(170)
        self.yxsj_widget.setContentsMargins(10, 0, 0, 0)
        self.yxsj_layout = QHBoxLayout(self.yxsj_widget)
        self.yxsj_layout.setSpacing(10)
        self.yxsj_layout.setContentsMargins(10, 0, 0, 0)




        # 将第二行添加到右边布局
        right_layout.addWidget(second_row_widget)

        # 右边布局容器
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # 将左边和右边布局添加到顶部布局
        top_layout.addWidget(left_widget)
        top_layout.addWidget(right_widget)

        # 设置顶部布局
        top_page.setLayout(top_layout)

        return top_page



    def create_button_layout(self):
        """创建按钮布局，放置五个横向排列的按钮"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(0)  # 设置按钮之间的间距为 10 像素
        button_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 10 像素

        # 添加五个按钮
        return button_layout

    def create_bottom_pages(self):
        """创建底部页面，分为左右两部分"""
        bottom_pages = QWidget()

        # 创建底部布局（横向排列）
        layout = QHBoxLayout()
        layout.setSpacing(0)  # 设置布局的间距为 0
        layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 0

        # 创建左边页面（表格）
        left_page = self.create_left_page()
        layout.addWidget(left_page)

        # 创建右边页面（输入框）
        right_page = self.create_right_page()
        layout.addWidget(right_page)

        # 设置底部布局
        bottom_pages.setLayout(layout)
        return bottom_pages

    def create_left_page(self):
        """创建左边页面，放置一个表格"""
        left_page = QWidget()
        left_page.setFixedWidth(700)  # 设置左边页面的宽度为 630 像素
        left_page.setStyleSheet("background-color: white;")  # 设置背景颜色

        # 创建布局
        layout = QVBoxLayout()
        layout.setSpacing(0)  # 设置布局的间距为 0
        layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 0

        self.win = Windowtable(self)

        # 将表格添加到布局
        layout.addWidget(self.win)
        left_page.setLayout(layout)
        return left_page

    def create_right_page(self):
        """创建右边页面，放置输入框"""
        right_page = QWidget()
        right_page.setStyleSheet("background-color: #e6f0fc;")  # 设置背景颜色
        page_layout = QVBoxLayout(right_page)
        # 创建布局


        self.right_layout = QVBoxLayout()
        self.right_layout.setSpacing(15)  # 设置输入框之间的间距为 10 像素
        self.right_layout.setContentsMargins(0, 0, 0, 0)  # 设置顶部边距为 10 像素
        self.right_layout.setAlignment(Qt.AlignTop)  # 设置左对齐
        #添加说明
        #sm_widget = QWidget()
        #sm_widget.setFixedWidth(250)
        #sm_layout = QHBoxLayout(sm_widget)
        #ql=QLabel("说明：昨日收盘流通市值。")
        #ql.setStyleSheet("color: red;")  # 设置背景颜色
        #sm_layout.addWidget(ql)
        #self.right_layout.addWidget(sm_widget)



        # 添加涨停后炸板再封板时买入
        #ztzbfb_widget = QWidget()
        #ztzbfb_layout = QHBoxLayout(ztzbfb_widget)
        #ztzbfb_layout.setSpacing(0)  # 设置组件之间的间距为 0 像素
        #ztzbfb_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 0
        #ztzbfb_widget.setFixedWidth(390)
        # bdjjztb_widget.setStyleSheet("border: 1px solid black; border-radius: 5px; padding: 5px;")
        #self.ztzbfb = LittleSwitchButton()
        #self.ztzbfb_label = QLabel(" 涨停后炸板再次封板时买入")
        #self.ztzbfb_label.setStyleSheet("font-size: 14px;")
        # self.dyzb.stateChanged.connect(self.on_dyzb_state_changed)
        #ztzbfb_layout.addWidget(self.ztzbfb)  # 添加新的 QCheckBox
        #ztzbfb_layout.addWidget(self.ztzbfb_label)  # 添加新的 QCheckBox
        #self.right_layout.addWidget(ztzbfb_widget)
        # 涨停后炸板再封板时买入

        # 添加说明结束
        # 第三行：流通市值输入框
        market_value_widget = QWidget()
        market_value_widget.setFixedWidth(360)  # 设置 QWidget 的宽度为 250 像素
        market_value_layout = QHBoxLayout(market_value_widget)
        market_value_layout.setSpacing(0)  # 设置组件之间的间距为 0 像素
        market_value_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 0

        # 涨幅开始
        zf_widget = QWidget()
        zf_widget.setFixedWidth(310)  # 设置 QWidget 的宽度为 200 像素
        zf_layout = QHBoxLayout(zf_widget)
        zf_layout.setSpacing(0)  # 设置组件之间的间距为 0 像素
        zf_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 0
        self.zf_switch = LittleSwitchButton()
        self.zf_switch.switched_on.connect(self.enable_zf_inputs)
        self.zf_switch.switched_off.connect(self.disable_zf_inputs)
        zf_layout.addWidget(self.zf_switch)
        zf = QLabel(" 涨幅: ")
        zf.setStyleSheet("font-size: 14px;")
        zf_layout.addWidget(zf)
        # 输入框 1
        self.zf_min = QLineEdit()
        self.zf_min.setStyleSheet("background-color: white;")
        self.zf_min.setFixedWidth(80)  # 设置输入框宽度
        self.zf_min.setValidator(QDoubleValidator())  # 限制只能输入数字
        zf_layout.addWidget(self.zf_min)
        # 标签

        zfsl_label = QLabel("% 至 ")
        zfsl_label.setStyleSheet("font-size: 14px;")
        zf_layout.addWidget(zfsl_label)

        # 输入框 2
        self.zf_max = QLineEdit()
        self.zf_max.setStyleSheet("background-color: white;")
        self.zf_max.setFixedWidth(80)  # 设置输入框宽度
        self.zf_max.setValidator(QDoubleValidator())  # 限制只能输入数字
        zf_layout.addWidget(self.zf_max)
        self.right_layout.addWidget(zf_widget)
        zfzhsljs_label = QLabel("%时买入")
        zfzhsljs_label.setStyleSheet("font-size: 14px;")
        zf_layout.addWidget(zfzhsljs_label)
        # 涨幅结束



        # 比开盘涨幅开始
        hsl_widget = QWidget()
        hsl_widget.setFixedWidth(360)  # 设置 QWidget 的宽度为 200 像素
        hsl_layout = QHBoxLayout(hsl_widget)
        hsl_layout.setSpacing(0)  # 设置组件之间的间距为 0 像素
        hsl_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 0
        self.yfzzf_switch = LittleSwitchButton()
        self.yfzzf_switch.switched_on.connect(self.enable_hsl_inputs)
        self.yfzzf_switch.switched_off.connect(self.disable_hsl_inputs)
        hsl_layout.addWidget( self.yfzzf_switch)
        hsl = QLabel(" 相比开盘价涨幅: ")
        hsl.setStyleSheet("font-size: 14px;")
        hsl_layout.addWidget(hsl)
        # 输入框 1
        self.yfzzf_min = QLineEdit()
        self.yfzzf_min.setStyleSheet("background-color: white;")
        self.yfzzf_min.setFixedWidth(80)  # 设置输入框宽度
        self.yfzzf_min.setValidator(QDoubleValidator())  # 限制只能输入数字
        hsl_layout.addWidget(self.yfzzf_min)
        # 标签

        zhsl_label = QLabel("% 至 ")
        zhsl_label.setStyleSheet("font-size: 14px;")
        hsl_layout.addWidget(zhsl_label)

        # 输入框 2
        self.yfzzf_max = QLineEdit()
        self.yfzzf_max.setStyleSheet("background-color: white;")
        self.yfzzf_max.setFixedWidth(80)  # 设置输入框宽度
        self.yfzzf_max.setValidator(QDoubleValidator())  # 限制只能输入数字
        hsl_layout.addWidget(self.yfzzf_max)
        self.right_layout.addWidget(hsl_widget)
        zhsljs_label = QLabel("%时买入")
        zhsljs_label.setStyleSheet("font-size: 14px;")
        hsl_layout.addWidget(zhsljs_label)
        # 比开盘涨幅结束




        # 股价输入框
        price_widget = QWidget()
        price_widget.setFixedWidth(280)  # 设置 QWidget 的宽度为 200 像素
        price_layout = QHBoxLayout(price_widget)
        price_layout.setSpacing(0)  # 设置组件之间的间距为 0 像素
        price_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为 0

        self.price_switch = LittleSwitchButton()
        self.price_switch.switched_on.connect(self.enable_price_inputs)
        self.price_switch.switched_off.connect(self.disable_price_inputs)
        price_layout.addWidget(self.price_switch)
        zrspjj = QLabel(" 股价: ")
        zrspjj.setStyleSheet("font-size: 14px;")
        price_layout.addWidget(zrspjj)
        # 输入框 1
        self.price_min = QLineEdit()
        self.price_min.setStyleSheet("background-color: white;")
        self.price_min.setFixedWidth(80)  # 设置输入框宽度
        self.price_min.setPlaceholderText("最低价")  # 设置占位符文本
        self.price_min.setValidator(QDoubleValidator())  # 限制只能输入数字
        price_layout.addWidget(self.price_min)
        # 标签

        z_label = QLabel(" 至")
        z_label.setStyleSheet("font-size: 14px;")
        price_layout.addWidget(z_label)

        # 输入框 2
        self.price_max = QLineEdit()
        self.price_max.setPlaceholderText("最高价")  # 设置占位符文本
        self.price_max.setStyleSheet("background-color: white;")
        self.price_max.setFixedWidth(80)  # 设置输入框宽度
        self.price_max.setValidator(QDoubleValidator())  # 限制只能输入数字

        mr_label = QLabel("时买入")
        mr_label.setStyleSheet("font-size: 14px;")
        price_layout.addWidget(z_label)
        price_layout.addWidget(self.price_max)
        price_layout.addWidget(mr_label)
        self.right_layout.addWidget(price_widget)
        # 昨日收盘价结束



        #时间范围开始
        dbsjfw_widget = QWidget()
        dbsjfw_widget.setFixedWidth(350)
        dbsjfw_layout = QHBoxLayout(dbsjfw_widget)
        dbsjfw_layout.setAlignment(Qt.AlignLeft)
        dbsjfw_layout.setSpacing(0)
        dbsjfw_layout.setContentsMargins(0, 0, 0, 0)
        dbsj_label=QLabel("买入时间范围：")
        dbsj_label.setStyleSheet("font-size: 14px;")
        dbsjfw_layout.addWidget(dbsj_label)

        # 第一个输入框（起始时间）
        self.start_time_spinbox = TimeSpinBox()
        self.start_time_spinbox.valueChanged.connect(self.on_start_time_changed)
        self.start_time_spinbox.setFixedHeight(25)
        self.start_time_spinbox.setFixedWidth(80)
        self.start_time_spinbox.setStyleSheet("background-color: white;")
        self.start_time_spinbox.setValue(9 * 60 + 30)  # 初始值 09:30
        dbsjfw_layout.addWidget(self.start_time_spinbox)
        dbsjfw2_label=QLabel(" 至 ")
        dbsjfw2_label.setStyleSheet("font-size: 14px;")
        dbsjfw_layout.addWidget(dbsjfw2_label)
        # 第二个输入框（结束时间）
        self.end_time_spinbox = TimeSpinBox()
        self.end_time_spinbox.valueChanged.connect(self.on_end_time_changed)
        self.end_time_spinbox.setFixedHeight(25)
        self.end_time_spinbox.setFixedWidth(80)
        self.end_time_spinbox.setStyleSheet("background-color: white;")
        self.end_time_spinbox.setValue(15 * 60 + 0)  # 初始值 10:00
        dbsjfw_layout.addWidget(self.end_time_spinbox)
        self.right_layout.addWidget(dbsjfw_widget)
        # 时间范围结束

        #买入时间控制
        dbsjkz_widget = QWidget()
        dbsjkz_widget.setFixedWidth(400)
        dbsjkz_layout = QHBoxLayout(dbsjkz_widget)
        dbsjkz_layout.setAlignment(Qt.AlignLeft)
        dbsjkz_layout.setSpacing(10)
        dbsjkz_layout.setContentsMargins(0, 0, 0, 0)
        #上午半小时
        self.swbxs_button = QPushButton("开盘半小时")
        self.swbxs_button.clicked.connect(self.on_swbxs_button_clicked)
        self.swbxs_button.setStyleSheet(get_button_style())
        self.swbxs_button.setFixedSize(92, 25)
        dbsjkz_layout.addWidget(self.swbxs_button)
        #上午一小时
        self.swyxs_button = QPushButton("开盘一小时")
        self.swyxs_button.clicked.connect(self.on_swyxs_button_clicked)
        self.swyxs_button.setStyleSheet(get_button_style())
        self.swyxs_button.setFixedSize(92, 25)
        dbsjkz_layout.addWidget(self.swyxs_button)

        # 上午
        self.sw_button = QPushButton("上午")
        self.sw_button.clicked.connect(self.on_sw_button_clicked)
        self.sw_button.setStyleSheet(get_button_style())
        self.sw_button.setFixedSize(50, 25)
        dbsjkz_layout.addWidget(self.sw_button)

        # 下午
        self.xw_button = QPushButton("下午")
        self.xw_button.clicked.connect(self.on_xw_button_clicked)
        self.xw_button.setStyleSheet(get_button_style())
        self.xw_button.setFixedSize(50, 25)
        dbsjkz_layout.addWidget(self.xw_button)

        # 全天
        self.qt_button = QPushButton("全天")
        self.qt_button.clicked.connect(self.on_qt_button_clicked)
        self.qt_button.setStyleSheet(get_button_style())
        self.qt_button.setFixedSize(50, 25)
        dbsjkz_layout.addWidget(self.qt_button)


        self.right_layout.addWidget(dbsjkz_widget)







        # 添加一个占位符，确保输入框紧贴顶部
        #spacer = QWidget()
        #spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.right_layout.addWidget(spacer)

        page_layout.addLayout(self.right_layout)

        #打板提示信息
        right_bottom_Widget=QWidget()
        right_bottom_Widget.setFixedHeight(170)
        right_bottom_Widget.setStyleSheet("background-color: white;")  # 设置背景颜色
        right_bottom_layout = QHBoxLayout(right_bottom_Widget)
        self.q_list=QListWidget()


        right_bottom_layout.addWidget(self.q_list)
        page_layout.addWidget(right_bottom_Widget)



        return right_page

    def clear_layout(self,layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())




    def on_checkbox_all_changed(self, state):
        """全选复选框状态变化时的槽函数"""
        # 如果全选复选框被选中
        if state:
            # 将其他三个复选框设置为不可操作并选中
            self.checkbox_main.setChecked(True)
            self.checkbox_main.setEnabled(False)
            self.checkbox_gem.setChecked(True)
            self.checkbox_gem.setEnabled(False)
            self.checkbox_star.setChecked(True)
            self.checkbox_star.setEnabled(False)
        else:
            # 如果全选复选框未选中
            self.checkbox_main.setChecked(False)
            self.checkbox_main.setEnabled(True)
            self.checkbox_gem.setChecked(False)
            self.checkbox_gem.setEnabled(True)
            self.checkbox_star.setChecked(False)
            self.checkbox_star.setEnabled(True)

            #self.save_data_by_thread()

    #时间转换
    def minutes_to_time_str(minutes):
        if not isinstance(minutes, int) or minutes < 0 or minutes >= 1440:
            raise ValueError("分钟数必须是0到1439之间的整数")
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02}:{mins:02}"

    # 打板按钮
    def on_switch_on(self):
        if self.ceshi_zt!=1:
            self.switch_button.is_checked = False
            QMessageBox.warning(self, "警告", "请测试 连接券商 按钮，按钮变成红色才能正常交易！")
            return

        # 新增验证：至少有一个条件被选中且输入有效
        if not (self.zf_switch.is_checked or self.yfzzf_switch.is_checked or self.price_switch.is_checked):
            QMessageBox.warning(self, "输入错误", "必须至少启用一个条件（涨幅、一分钟涨幅或股价）！")
            self.switch_button.is_checked = False
            return

        # 检查已启用条件的输入是否有效
        error_messages = []
        if self.zf_switch.is_checked:
            if not self.zf_min.text().strip() or not self.zf_max.text().strip():
                error_messages.append("涨幅范围不能为空")
        if self.yfzzf_switch.is_checked:
            if not self.yfzzf_min.text().strip() or not self.yfzzf_max.text().strip():
                error_messages.append("一分钟涨幅范围不能为空")
        if self.price_switch.is_checked:
            if not self.price_min.text().strip() or not self.price_max.text().strip():
                error_messages.append("股价范围不能为空")

        if error_messages:
            QMessageBox.warning(self, "输入错误", "\n".join(error_messages))
            self.switch_button.is_checked = False
            return


        # 新增输入验证
        if not self.validate_input_ranges():
            self.switch_button.is_checked = False
            return

        if self.zh_lx is None:
            self.switch_button.is_checked = False
            self.disable_checkboxes_and_inputs()  # 禁用所有的输入框
            QMessageBox.warning(self, "警告", "你无权限，请重新登录或者联系系统管理员（左侧侧边栏查看联系方式）！")
            return
        selected_data1 = []
        # 获取列表中所有数据
        for row in range(self.win._model.rowCount()):
            # 获取第一列的复选框
            checkbox_item = self.win._model.item(row, 0)
            if checkbox_item is not None and checkbox_item.checkState() == Qt.Checked:
                # 如果复选框被选中，获取第二列的股票代码
                code_item = self.win._model.item(row, 2)  # 第二列的索引是 2，获取code
                selected_data1.append(code_item.text())

        if  len(selected_data1)==0:
            #self.disable_checkboxes_and_inputs()  #禁用所有的输入框
            self.switch_button.is_checked = False
            QMessageBox.warning(self, "警告", "请选择要买的股票！")
            return

        selected_data = {}


            #jon存放选股条件
            # 获取各个复选框的选中状态
        jon = {}
        bk = []
        main_selected = self.checkbox_main.isChecked()
        if main_selected:
            main = self.checkbox_main.text()
            bk.append(main)
        gem_selected = self.checkbox_gem.isChecked()
        if gem_selected:
            gem = self.checkbox_gem.text()
            bk.append(gem)

        # 北交所
        star_selected = self.checkbox_star.isChecked()
        if star_selected:
            star = self.checkbox_star.text()
            bk.append(star)
        jon['bk'] = bk



        # 获取输入框的值
        mzgpmre_value = self.mzgpmre_input.text().strip().replace(",", "")  # 每只股票买入金额

        zzje_value = self.zzje_input.text().strip().replace(",", "")  # 总资金

        # 将输入框的值加入字典
        jon['mzgpmrje'] = mzgpmre_value.strip()
        if len( zzje_value.strip())==0:
            jon['zzje'] = "0"
        else:
            jon['zzje']=zzje_value.strip()
        #涨停后炸板买入作废
        #if self.ztzbfb.is_checked == True:
            #jon['ztzbfb'] = ""

        if self.zf_switch.is_checked == True:
            zf_min = self.zf_min.text().strip()  # 最小市值
            zf_max = self.zf_max.text().strip()  # 最大市值
            if len(zf_min) > 0:
                jon['zf_min'] = zf_min.strip()
            if len(zf_max) > 0:
                jon['zf_max'] = zf_max.strip()

        if self.price_switch.is_checked == True:
            price_min = self.price_min.text().strip()  # 最低股价
            price_max = self.price_max.text().strip()  # 最高股价
            if len(price_min) > 0:
                jon['price_min'] = price_min.strip()
            if len(price_max) > 0:
                jon['price_max'] = price_max.strip()

        # 换手率
        if self.yfzzf_switch.is_checked == True:
            yfzzf_min = self.yfzzf_min.text().strip()
            yfzzf_max = self.yfzzf_max.text().strip()
            if len(yfzzf_min) > 0:
                jon['yfzzf_min'] = yfzzf_min.strip()
            if len(yfzzf_max) > 0:
                jon['yfzzf_max'] = yfzzf_max.strip()

        # 获取“打最先涨停的前 N 个板”和“有效期”的选择框值
        first_limit_value = self.first_limit_combo.currentText().strip()  # 打最先涨停的前 N 个板
        # 存储选择框的值
        jon['zxzt_total'] = first_limit_value

        # 时间范围
        jon["start_time"] = self.start_time_spinbox.value()
        jon["end_time"] = self.end_time_spinbox.value()
        jon["buysz"]=self.buysz=self.sell_position_combo.currentText()


        #获取符合条件股票数据
        # 初始化一个空列表，用于存储选中的股票代码

        code_data = []
        # 遍历表格的每一行
        for row in range(self.win._model.rowCount()):
            # 获取第一列的复选框
            checkbox_item = self.win._model.item(row, 0)
            if checkbox_item is not None and checkbox_item.checkState() == Qt.Checked:
                # 如果复选框被选中，获取第二列的股票代码
                code_item = self.win._model.item(row, 2)  # 第二列的索引是 2，获取code
                price_item = self.win._model.item(row, 10)  #第十列是昨天的收盘价
                ztzt_item = self.win._model.item(row, 6)  # 涨停板数量是6
                ltsz_item = self.win._model.item(row, 7)  # 流通市值7
                hsl_item = self.win._model.item(row, 5)  # 换手率5
                if code_item is not None and price_item is not None and ztzt_item is not None and ltsz_item is not None :
                    code=code_item.text()
                    zr_price=price_item.text()
                    ztzt=ztzt_item.text()
                    ltsz=ltsz_item.text()
                    hsl = hsl_item.text()

                    selected_data[code_item.text()] = zr_price

        #print(f"selected_data选好的：{selected_data}")

        if not selected_data:
            QMessageBox.warning(self, "警告", "没有符合条件的股票，请你重新选择！")
            self.switch_button.is_checked = False
            return


        # 调用 DB1 类并传递选中的股票代码
        if not self.db1:
            self.db1=tjd_db()
        db1=self.db1
        # 连接 tjd_db 的信号到 on_switch_off 方法
        self.db1.switch_off_signal.connect(self.on_db1_stopped)

        db1.init_db_data(selected_data,self.qmt_trader,jon,True,self.switch_button,self.dbsm2,self,self.buysz)
        # 连接打板程序信号，用于关闭switch_burtton
        #修改打了几个板的状态
        self.db1.zxzt_total_changed.connect(self.update_dbsm2)  # 连接信号
        # 金额不足提示
        self.jebz_info.connect(self.jebz_info_add)  # 连接信号到 jebz_info


        #耗时操作，使用线程
        thread = threading.Thread(target=self.save_dbi_data_thread, args=(jon,selected_data))
        thread.start()

        self.disable_checkboxes_and_inputs()


    #修改打了几个板的状态
    def update_dbsm2(self, value):
        """更新已打板数量的显示"""
        self.dbsm2.setText(str(value))

    def on_db1_stopped(self):
        # 在主线程中更新 UI
        self.switch_button.is_checked = False  # 修改按钮状态
        self.enable_checkboxes_and_inputs()  # 启用其他控件


    def save_dbi_data_thread(self,jon,selected_data):
        # 获取当前日期
        today = datetime.today()
        json_str = str(json.dumps(jon))
        rq = today.strftime("%Y-%m-%d")
        dblx = "tjd"
        deal = DeaiClientData()
        action = "save_db_data"
        deal.save_db_data(action, json_str, rq, self.username, selected_data, dblx)


    # 关闭打板按钮
    def on_switch_off(self):
        if  self.db1:
            self.db1.set_enabled(False)
            self.switch_button.is_checked = False
            self.enable_checkboxes_and_inputs()

    #一点击就保存数据
    def save_data_by_thread(self):
        self.update_thread = threading.Thread(target=self.save_button_clicked)
        self.update_thread.start()

    #保存所有数据，修改任何一项都要执行保存动作
    def save_button_clicked(self):
        """启用打板按钮点击事件的槽函数"""

        # 新增输入验证
        if not self.validate_input_ranges():
            self.switch_button.is_checked = False
            return

        selected_data = []
        #获取列表中所有数据
        for row in range(self.win._model.rowCount()):
            # 获取第一列的复选框
            code_item = self.win._model.item(row, 2)  # 第二列的索引是 2，获取code
            selected_data.append(code_item.text())


        # 获取各个复选框的选中状态
        jon={}
        bk=[]
        main_selected = self.checkbox_main.isChecked()
        if main_selected:
            main= self.checkbox_main.text()

            bk.append(main)
        gem_selected = self.checkbox_gem.isChecked()
        if gem_selected:
            gem =self.checkbox_gem.text()
            bk.append(gem)

        #北交所
        star_selected = self.checkbox_star.isChecked()
        if star_selected:
            star =self.checkbox_star.text()
            bk.append(star)
        jon['bk']=bk


        db = []
        # 获取首板、二板、三板复选框的选中状态

        mzgpmre_value = self.mzgpmre_input.text().strip().replace(",", "")   # 每只股票买入金额
        # 将输入框的值加入字典
        jon['mzgpmrje'] = mzgpmre_value.strip()

        zzje_value = self.zzje_input.text().strip().replace(",", "")  # 总资金
        if len(zzje_value.strip()) == 0:
            jon['zzje'] = "0"
        else:
            jon['zzje'] = zzje_value.strip()
        #涨停后炸板买入作废
       # if self.ztzbfb.is_checked==True:
            #jon['ztzbfb'] =""

        if self.zf_switch.is_checked==True:
            zf_min = self.zf_min.text().strip()  # 最小市值
            zf_max = self.zf_max.text().strip()  # 最大市值
            if len(zf_min)>0:
                jon['zf_min'] = zf_min.strip()
            if  len(zf_max)>0:
                jon['zf_max'] = zf_max.strip()


        if self.price_switch.is_checked == True:
            price_min = self.price_min.text().strip()  # 最低股价
            price_max = self.price_max.text().strip()  # 最高股价
            if len(price_min)>0:
                jon['price_min'] = price_min.strip()
            if  len(price_max)>0:
                jon['price_max'] = price_max.strip()

        # 换手率
        if self.yfzzf_switch.is_checked == True:
            yfzzf_min = self.yfzzf_min.text().strip()
            yfzzf_max = self.yfzzf_max.text().strip()
            if len(yfzzf_min) > 0:
                jon['yfzzf_min'] = yfzzf_min.strip()
            if len(yfzzf_max) > 0:
                jon['yfzzf_max'] = yfzzf_max.strip()


        # 买几个股
        first_limit_value = self.first_limit_combo.currentText().strip()  # 打最先涨停的前 N 个板
        # 存储选择框的值
        jon['zxzt_total'] = first_limit_value
        jon["buysz"] = self.buysz = self.sell_position_combo.currentText()
        #时间范围
        jon["start_time_spinbox"]=self.start_time_spinbox.value()
        jon["end_time_spinbox"] = self.end_time_spinbox.value()

        # 获取当前日期
        today = datetime.today()
        json_str = str(json.dumps(jon))
        rq = today.strftime("%Y-%m-%d")
        dblx="tjd"
        deal=DeaiClientData()
        action = "save_db_data"
        message = deal.save_db_data(action, json_str,rq,self.username,selected_data,dblx)
        if message["message"]=="success":
            QMessageBox.information(self, "成功", "保存成功！")

    # 禁用所有的 checkbox 和输入框
    # 禁用所有的 checkbox 和输入框
    def disable_checkboxes_and_inputs(self):
        # 顶部页面的 checkbox 和输入框
        checkboxes_top = [self.checkbox_all, self.checkbox_main, self.checkbox_gem, self.checkbox_star ]
        inputs_top = [self.mzgpmre_input, self.zzje_input]

        for checkbox in checkboxes_top:
            checkbox.setEnabled(False)
        for input_field in inputs_top:
            input_field.setEnabled(False)
        # 底部页面的输入框
        inputs_bottom = [self.zf_min, self.zf_max, self.price_min, self.price_max,
                         self.yfzzf_min, self.yfzzf_max, self.start_time_spinbox, self.end_time_spinbox]
        if hasattr(self, 'capital_input'):
            inputs_bottom.append(self.capital_input)
        if hasattr(self, 'myfd_input'):
            inputs_bottom.append(self.myfd_input)
        for input_field in inputs_bottom:
            input_field.setEnabled(False)
            # 遍历时检查控件是否有效
        for input_field in inputs_bottom:
            if input_field is not None and input_field.isWidgetType():
                try:
                    input_field.setEnabled(False)
                except RuntimeError:
                    # 如果对象已被删除，跳过
                    pass

        # 买入时机选择框
        self.first_limit_combo.setEnabled(False)
        self.combo_box_qmt.setEnabled(False)
        # 禁用表格中的行复选框按钮
        for row in range(self.win._model.rowCount()):
            checkbox_item = self.win._model.item(row, 0)
            if checkbox_item:
                checkbox_item.setFlags(checkbox_item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)

        # 禁用全选、取消选中、清空按钮
        self.win.select_all_button.setEnabled(False)
        self.win.unselect_all_button.setEnabled(False)
        self.win.clear_button.setEnabled(False)
        self.win.delbu.setEnabled(False)
        # 禁用所有按钮
        buttons = [self.save_button, self.test_button,
                   self.swbxs_button, self.swyxs_button, self.sw_button,
                   self.xw_button, self.qt_button]
        for button in buttons:
            button.setEnabled(False)

        switchs = [ self.zf_switch, self.price_switch, self.yfzzf_switch]
        for switch in switchs:
            switch.setEnabled(False)  # 仅启用控件，保持当前状态


    def enable_checkboxes_and_inputs(self):
        # 顶部页面的 checkbox 和输入框
        checkboxes_top = [self.checkbox_all, self.checkbox_main, self.checkbox_gem, self.checkbox_star]
        inputs_top = [self.mzgpmre_input, self.zzje_input]

        for checkbox in checkboxes_top:
            checkbox.setEnabled(True)
        for input_field in inputs_top:
            input_field.setEnabled(True)
        switchs = [ self.zf_switch, self.price_switch, self.yfzzf_switch]
        for switch in switchs:
            switch.setEnabled(True)  # 仅启用控件，保持当前状态

        # 底部页面的输入框
        inputs_bottom = [self.zf_min, self.zf_max, self.price_min, self.price_max,
                         self.yfzzf_min, self.yfzzf_max, self.start_time_spinbox, self.end_time_spinbox]
        if hasattr(self, 'capital_input'):
            inputs_bottom.append(self.capital_input)
        if hasattr(self, 'myfd_input'):
            inputs_bottom.append(self.myfd_input)
        for input_field in inputs_bottom:
            input_field.setEnabled(True)

        # 买入时机选择框
        self.first_limit_combo.setEnabled(True)
        self.combo_box_qmt.setEnabled(True)

        # 启用表格中的行复选框按钮
        for row in range(self.win._model.rowCount()):
            checkbox_item = self.win._model.item(row, 0)
            if checkbox_item:
                checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)

        # 启用全选、取消选中、清空按钮
        self.win.select_all_button.setEnabled(True)
        self.win.unselect_all_button.setEnabled(True)
        self.win.clear_button.setEnabled(True)
        self.win.delbu.setEnabled(True)

        # 启用所有按钮
        buttons = [self.save_button, self.test_button,
                   self.swbxs_button, self.swyxs_button, self.sw_button,
                   self.xw_button, self.qt_button]
        for button in buttons:
            button.setEnabled(True)

    def validate_input_ranges(self):
        """验证所有启用的输入框范围是否有效"""
        # 在原有验证前添加：
        enabled_switches = sum([
            self.zf_switch.is_checked,
            self.yfzzf_switch.is_checked,
            self.price_switch.is_checked
        ])

        if enabled_switches > 1:
            QMessageBox.warning(self, "配置错误", "一次只能选择一个条件（涨幅、1分钟涨幅、股价）")
            return False
        if enabled_switches < 1:
            QMessageBox.warning(self, "配置错误", "必须至少选择一个条件")
            return False


        # 检查涨幅范围
        if self.zf_switch.is_checked:
            zf_min = self.zf_min.text().replace(',', '').strip()
            zf_max = self.zf_max.text().replace(',', '').strip()
            if not zf_min or not zf_max:
                QMessageBox.warning(self, "输入错误", "涨幅范围必须填写最小值和最大值！")
                return False
            try:
                if float(zf_min) >= float(zf_max):
                    QMessageBox.warning(self, "输入错误", "涨幅最小值必须小于最大值！")
                    return False
            except ValueError:
                QMessageBox.warning(self, "输入错误", "涨幅输入无效！")
                return False

        # 检查一分钟涨幅范围
        if self.yfzzf_switch.is_checked:
            yfzzf_min = self.yfzzf_min.text().replace(',', '').strip()
            yfzzf_max = self.yfzzf_max.text().replace(',', '').strip()
            if not yfzzf_min or not yfzzf_max:
                QMessageBox.warning(self, "输入错误", "一分钟涨幅范围必须填写最小值和最大值！")
                return False
            try:
                if float(yfzzf_min) >= float(yfzzf_max):
                    QMessageBox.warning(self, "输入错误", "一分钟涨幅最小值必须小于最大值！")
                    return False
            except ValueError:
                QMessageBox.warning(self, "输入错误", "一分钟涨幅输入无效！")
                return False

        # 检查股价范围
        if self.price_switch.is_checked:
            price_min = self.price_min.text().replace(',', '').strip()
            price_max = self.price_max.text().replace(',', '').strip()
            if not price_min or not price_max:
                QMessageBox.warning(self, "输入错误", "股价范围必须填写最小值和最大值！")
                return False
            try:
                if float(price_min) >= float(price_max):
                    QMessageBox.warning(self, "输入错误", "股价最小值必须小于最大值！")
                    return False
            except ValueError:
                QMessageBox.warning(self, "输入错误", "股价输入无效！")
                return False

        return True