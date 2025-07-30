import threading
from PySide6.QtCore import QThread, Signal, QTimer, QObject, QMetaObject
from concurrent.futures import ThreadPoolExecutor
from santou.DeaiClientData import DeaiClientData
import json
from santou.account import Account
from santou.trading_time import ChinaHolidays
from datetime import datetime
from santou.tjdmr.TradingHandler import TradingHandler
from santou.logging.log import logger
from decimal import Decimal, ROUND_HALF_UP
from PySide6.QtCore import Qt
from threading import Lock
class tjd_db(QObject):
    _instance = None
    price_list = None
    # 用于处理按钮关闭操作
    zxzt_total_changed = Signal(int)
    # 定义一个信号，用于通知 tjd_ym 类执行 on_switch_off 方法
    switch_off_signal = Signal()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(tjd_db, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        if not hasattr(self, '_initialized'):
            self.zxzt_lock = Lock()  # 新增锁
            self._initialized = True
            self.worker_thread = None
            self.strategy_lock = threading.Lock()  # 策略层全局锁
            self.thread_pool = ThreadPoolExecutor(max_workers=10)  # 创建线程池，可根据实际情况调整最大工作线程数
            self._thread_pool_closed = False  # 新增标志，用于记录线程池是否关闭

    def decrease_zxzt_total(self):
        self.zxzt_total -= 1
        self.zxzt_total_changed.emit(self.zxzt_total)
        if self.zxzt_total == 0:
            self.set_enabled(False)

    def init_db_data(self, gpss, qmt, jon, is_enabled, switchButton, first_limit_combo, db_ym1,buysz):
        self.is_enabled = is_enabled
        self.timer = None
        self.qmt = qmt
        self.jon = jon
        self.buysz = buysz
        self.price_list = gpss
        self.db_ym1 = db_ym1
        self.zxzt_total = int(jon["zxzt_total"])
        self.zzje = float(jon["zzje"])
        self.zt_gps = []


        now = datetime.now()
        self.db_sq_time = now.time()
        self.db_sq_day = now.date()
        if self.price_list:
            self.start_timer()

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.zx_db)
        self.timer.start(Account().get_time())

    def set_enabled(self, enabled):
        self.is_enabled = enabled
        if not enabled:
            self.stop_operation()

    def findp_rice(self, price_list, code):
        if price_list is None or len(price_list) == 0:
            return None
        return float(price_list.get(code))

    def add_exchange_suffix(self, stock_code):
        stock_code = stock_code.strip()
        if stock_code.endswith(('.SH', '.SZ', '.BJ')):
            return stock_code
        elif stock_code.startswith(('300', '301', '00')):  # 创业板 + 深主板
            return stock_code + '.SZ'
        elif stock_code.startswith(('60', '688')):  # 沪主板 + 科创板
            return stock_code + '.SH'
        elif stock_code.startswith(('8', '43', '83')):  # 北交所 + 老三板
            return stock_code + '.BJ'
        return stock_code

    def stop_jy(self):
        now = datetime.now()
        current_time = now.time()
        current_day = now.date()
        ho = ChinaHolidays()
        is_non_trading_day = ho.is_china_stock_trading_time()
        if not is_non_trading_day and self.db_sq_day == current_day:
            # 说明今天执行了交易，不是三点后发的
            if self.db_sq_time < datetime.strptime("15:00:00", "%H:%M:%S").time():
                if current_time >= datetime.strptime("15:00:00", "%H:%M:%S").time():
                    print("今天是交易日，过了三点结束程序")
                    self.set_enabled(False)
        if not is_non_trading_day and self.db_sq_day < current_day:
            if current_time >= datetime.strptime("15:00:00", "%H:%M:%S").time():
                print("下个交易日的下午三点已过，结束交易程序")
                self.set_enabled(False)

    def zx_db(self):

        if not self.is_enabled:
            return
        self.stop_jy()
        if not self.is_enabled:
            return
        if ChinaHolidays().is_china_stock_trading_time():
            print("今天不是交易日")
            return
        if self.price_list is None or len(self.price_list) == 0:
            self.set_enabled(False)
            return
        if not self.deal_jysj():
            print("非交易时间段")
            return
        if self.zxzt_total == 0:
            self.set_enabled(False)
            return

        # 检查线程池是否关闭
        if self._thread_pool_closed:
            self.thread_pool = ThreadPoolExecutor(max_workers=10)  # 重新创建线程池
            self._thread_pool_closed = False

        # 提交任务到线程池
        self.thread_pool.submit(self.run_worker)

    def run_worker(self):
        worker = Worker(self, self.db_ym1, self.jon, self.zt_gps,self.buysz)
        worker.finished.connect(self.worker_finished)
        worker.run()

    def worker_finished(self):
        pass

    def deal_jysj(self):
        try:
            start_time = int(self.jon["start_time"])
            end_time = int(self.jon["end_time"])

            mon_start_time = 9 * 60 + 30
            mon_end_time = 11 * 60 + 30
            afton_start_time = 13 * 60
            afton_end_time = 15 * 60
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            today_total_minutes = current_hour * 60 + current_minute
            is_in_morning_trading = mon_start_time <= today_total_minutes <= mon_end_time
            is_in_afternoon_trading = afton_start_time <= today_total_minutes <= afton_end_time
            is_in_custom_trading = start_time <= today_total_minutes <= end_time
            print((is_in_morning_trading or is_in_afternoon_trading) and is_in_custom_trading)
            return (is_in_morning_trading or is_in_afternoon_trading) and is_in_custom_trading
        except (KeyError, ValueError):
            logger.error('tjd_db:dealjysj', exc_info=True)
            return False

    def stop_operation(self):
        if self.timer:
            self.timer.stop()
            self.timer = None
        self.price_list = None
        self.is_enabled = False
        self.db_sq_time = None

        # 触发信号，通知 tjd_ym 类执行 on_switch_off 方法
        self.switch_off_signal.emit()

        if not self._thread_pool_closed:
            # 使用主线程来关闭线程池
            QTimer.singleShot(0, self._safe_shutdown_thread_pool)


    def _safe_shutdown_thread_pool(self):
        """在主线程中安全关闭线程池"""
        if not self._thread_pool_closed:
            self.thread_pool.shutdown(wait=False)
            self._thread_pool_closed = True

class Worker(QObject):
    finished = Signal()

    def __init__(self, db1, db_ym1, jon, zt_gps,buysz):
        super().__init__()
        self.db1 = db1
        self.jon = jon
        self.buysz = buysz
        self.zt_gps = zt_gps
        self.db_ym1 = db_ym1
        self.trading_handler = TradingHandler()
        self.stock_executor = ThreadPoolExecutor(max_workers=5)  # 新增股票级线程池

    def run(self):

        gps = list(self.db1.price_list.keys())
        zh_lx=Account.zh_lx
        action = 'get_tick_datas'
        deal = DeaiClientData()
        try:
            data = deal.get_tick_datas(action, gps,zh_lx)
            if isinstance(data, str):
                data = json.loads(data)
        except Exception as e:
            logger.error('tjd_db:worker:run:获取实时数据或解析 JSON 时出错', exc_info=True)
            self.finished.emit()
            return
        buy_lx="tjd"
        if data is not None:
            for item in data:
                if self.db1.zxzt_total == 0:
                    self.db1.set_enabled(False)
                    self.finished.emit()
                    return
                # 为每只股票提交独立任务
                futures = [self.stock_executor.submit(self.process_stock, item, buy_lx) for item in data]
                # 等待所有股票处理完成
                for future in futures:
                    future.result()
        self.finished.emit()


    def process_stock(self, item, buy_lx):
        try:
            code = item['code']
            close = float(item['close'])
            zr_price = self.db1.findp_rice(self.db1.price_list, code)
            if zr_price is None:
                print(f"未找到代码 {code} 的昨日收盘价，跳过处理")
                return
            # 价格

            if "price_min" in self.jon and "price_max" not in self.jon:
                if len(self.jon["price_min"]) > 0:
                    if close >= float(self.jon["price_min"]):
                        buy_pice = self.find_buy_price(item, code, zr_price)
                        self.trading_handler.handle_trading(self.db1, code, buy_pice, self, buy_lx)

            if "price_min" not in self.jon and "price_max" in self.jon:
                if len(self.jon["price_max"]) > 0:
                    if close <= float(self.jon["price_max"]):
                        buy_pice = self.find_buy_price(item, code, zr_price)
                        self.trading_handler.handle_trading(self.db1, code, buy_pice, self, buy_lx)

            if "price_min" in self.jon and "price_max" in self.jon:
                if len(self.jon["price_max"]) > 0 and len(self.jon["price_min"]) > 0:
                    if close >= float(self.jon["price_min"]) and close <= float(self.jon["price_max"]):
                        buy_pice = self.find_buy_price(item, code, zr_price)
                        self.trading_handler.handle_trading(self.db1, code, buy_pice, self, buy_lx)

            # 涨幅
            if "zf_min" in self.jon and "zf_max" not in self.jon:
                if len(self.jon["zf_min"]) > 0:
                    current_change = ((close - zr_price) / zr_price) * 100  # 实际涨跌幅
                    if current_change >= float(self.jon["zf_min"]):
                        buy_pice = self.find_buy_price(item, code, zr_price)
                        self.trading_handler.handle_trading(self.db1, code, buy_pice, self, buy_lx)

            if "zf_min" not in self.jon and "zf_max" in self.jon:
                if len(self.jon["zf_max"]) > 0:
                    current_change = ((close - zr_price) / zr_price) * 100  # 实际涨跌幅
                    if current_change <= float(self.jon["zf_max"]):
                        buy_pice = self.find_buy_price(item, code, zr_price)
                        self.trading_handler.handle_trading(self.db1, code, buy_pice, self, buy_lx)

            if "zf_min" in self.jon and "zf_max" in self.jon:
                if len(self.jon["zf_max"]) > 0 and len(self.jon["zf_min"]) > 0:
                    current_change = ((close - zr_price) / zr_price) * 100  # 实际涨跌幅

                    if current_change >= float(self.jon["zf_min"]) and current_change <= float(self.jon["zf_max"]):
                        buy_pice = self.find_buy_price(item, code, zr_price)
                        self.trading_handler.handle_trading(self.db1, code, buy_pice, self, buy_lx)

            # 一分钟涨幅
            if "yfzzf_min" in self.jon and "yfzzf_max" not in self.jon:
                if len(self.jon["yfzzf_min"]) > 0:
                    one_min_zf = self.getrxsj_by_one_min(code)
                    close1 = float(one_min_zf["close1"])
                    close2 = float(one_min_zf["close2"])
                    current_change = ((close2 - close1) / close1) * 100  # 实际涨跌幅
                    if current_change >= float(self.jon["yfzzf_min"]):
                        buy_pice = self.find_buy_price(item, code, zr_price)
                        self.trading_handler.handle_trading(self.db1, code, buy_pice, self, buy_lx)

            if "yfzzf_min" not in self.jon and "yfzzf_max" in self.jon:
                if len(self.jon["yfzzf_max"]) > 0:
                    one_min_zf = self.getrxsj_by_one_min(code)
                    close1 = float(one_min_zf["close1"])
                    close2 = float(one_min_zf["close2"])
                    current_change = ((close2 - close1) / close1) * 100  # 实际涨跌幅
                    if current_change <= float(self.jon["yfzzf_max"]):
                        buy_pice = self.find_buy_price(item, code, zr_price)
                        self.trading_handler.handle_trading(self.db1, code, buy_pice, self, buy_lx)

            if "yfzzf_min" in self.jon and "yfzzf_max" in self.jon:
                if len(self.jon["yfzzf_max"]) > 0 and len(self.jon["yfzzf_min"]) > 0:
                    one_min_zf = self.getrxsj_by_one_min(code)
                    close1 = float(one_min_zf["close1"])
                    close2 = float(one_min_zf["close2"])
                    current_change = ((close2 - close1) / close1) * 100  # 实际涨跌幅
                    print(current_change)
                    print(float(self.jon["yfzzf_min"]))
                    print(float(self.jon["yfzzf_max"]))
                    if current_change >= float(self.jon["yfzzf_min"]) and current_change <= float(
                            self.jon["yfzzf_max"]):
                        buy_pice = self.find_buy_price(item, code, zr_price)

                        self.trading_handler.handle_trading(self.db1, code, buy_pice, self, buy_lx)
        except Exception as e:
            logger.error('tjd_db:worker:run:买入程序出错', exc_info=True)
            self.finished.emit()
            return

    #查一分钟的涨幅
    def getrxsj_by_one_min(self, code):
        zh_lx=Account.zh_lx
        action = 'getrxsj_by_one_min'
        deal = DeaiClientData()
        try:
            data = deal.getrxsj_by_one_min(action, code,zh_lx)
            if isinstance(data, str):
                data = json.loads(data)
            return data
        except Exception as e:
            logger.error('tjd_db:worker:run:getrxsj_by_one_min方法:获取实时数据或解析 JSON 时出错', exc_info=True)
            self.finished.emit()
            return

    def find_buy_price(self, tick,gpdm,zr_price):
        price = 0
        zt_price = self.zt_price(gpdm, float(zr_price))
        if self.buysz == "卖二":
            price = float(tick["ask2"])
            if price == 0:
                price = self.mr_price(tick,zr_price,gpdm)
        if self.buysz == "卖三":
            price = float(tick["ask3"])
            if price == 0:
                price = self.mr_price(tick,zr_price,gpdm)
        if self.buysz == "卖四":
            price = float(tick["ask4"])
            if price == 0:
                price = self.mr_price(tick,zr_price,gpdm)
        if self.buysz == "卖五":
            price = float(tick["ask5"])
            if price == 0:
                price = self.mr_price(tick,zr_price,gpdm)
        if self.buysz == "1%":
            price = float(tick["close"]) + (float(tick["close"]) * 0.01)
            if price >= zt_price:
                price = zt_price
        if self.buysz == "1.8%":
            price = float(tick["close"]) + (float(tick["close"]) * 0.018)
            if price >= zt_price:
                price = zt_price
        return price

    def mr_price(self, item, zr_price, gpdm):
        zt_price = self.zt_price(gpdm, float(zr_price))
        js_price = float(item["close"]) + (float(item["close"]) * 0.015)
        if js_price > zt_price:
            return zt_price
        return js_price

    def zt_price(self, gpdm, price):
        price_dec = Decimal(str(price))
        if gpdm.startswith(('300', '301', '688')):
            zt = price_dec * Decimal('1.20')
        elif gpdm.startswith(('00', '60')):
            zt = price_dec * Decimal('1.10')
        elif gpdm.startswith(('8', '4')):
            zt = price_dec * Decimal('1.30')
        return float(zt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
