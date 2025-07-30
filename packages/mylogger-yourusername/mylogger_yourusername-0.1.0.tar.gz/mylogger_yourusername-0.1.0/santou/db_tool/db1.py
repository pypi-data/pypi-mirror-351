import threading
from PySide6.QtCore import QThread, Signal, QTimer, QObject
from concurrent.futures import ThreadPoolExecutor
from santou.DeaiClientData import DeaiClientData
import json
from santou.account import Account
from santou.trading_time import ChinaHolidays
from datetime import datetime
from santou.db_tool.TradingHandler import TradingHandler
from santou.logging.log import logger
from decimal import Decimal, ROUND_HALF_UP
import time
class DB1(QObject):
    _instance = None
    price_list = None
    # 用于处理按钮关闭操作
    zxzt_total_changed = Signal(int)
    stopped = Signal()  # 新增信号
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DB1, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.worker_thread = None
            self.strategy_lock = threading.Lock()  # 策略层全局锁
            self.thread_pool = ThreadPoolExecutor(max_workers=10)  # 创建线程池，可根据实际情况调整最大工作线程数
            self._thread_pool_closed = False  # 新增标志，用于记录线程池是否关闭

    def decrease_zxzt_total(self):
        self.zxzt_total -= 1
        self.zxzt_total_changed.emit(self.zxzt_total)
        if  self.zxzt_total==0:
            print("set_enabled")
            self.set_enabled(False)

    def init_db_data(self, gpss, qmt, jon, is_enabled, switchButton, first_limit_combo, db_ym1):
        self.is_enabled = is_enabled
        self.timer = None
        self.qmt = qmt
        self.jon = jon
        self.price_list = gpss
        self.db_ym1 = db_ym1
        self.zxzt_total = int(jon["zxzt_total"])
        self.zzje = float(jon["zzje"])
        self.switch_button = switchButton
        self.zt_gps = []
        # 打板时清空
        first_limit_combo.setText("0")

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
        #self.set_enabled(False)
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
        worker = Worker(self, self.db_ym1, self.jon, self.zt_gps)
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
            # 如果选了打一字板，9：25开始执行，
            #if "dyzb" in self.jon:
               #dyzb = 565 <= today_total_minutes < 570
               #if dyzb:
                  #return dyzb

            is_in_morning_trading = mon_start_time <= today_total_minutes <= mon_end_time
            is_in_afternoon_trading = afton_start_time <= today_total_minutes <= afton_end_time
            is_in_custom_trading = start_time <= today_total_minutes <= end_time
            print((is_in_morning_trading or is_in_afternoon_trading) and is_in_custom_trading)
            return (is_in_morning_trading or is_in_afternoon_trading) and is_in_custom_trading
        except (KeyError, ValueError):
            logger.error('db1:dealjysj', exc_info=True)
            return False

    def stop_operation(self):
        if self.timer:
            self.timer.stop()
            self.timer = None
        self.price_list = None
        self.is_enabled = False
        self.db_sq_time = None
        # 发射信号，由主线程处理 UI 更新,通知给db_ym1
        self.stopped.emit()
        if not self._thread_pool_closed:
            self.thread_pool.shutdown(wait=False)  # 修改这里，设置wait=False
            self._thread_pool_closed = True  # 标记线程池已关闭



class Worker(QObject):
    finished = Signal()

    def __init__(self, db1, db_ym1, jon, zt_gps):
        super().__init__()
        self.db1 = db1
        self.jon = jon
        self.zt_gps = zt_gps
        self.db_ym1 = db_ym1
        self.trading_handler = TradingHandler()

    def run(self):
        start = time.perf_counter()  # 高精度计时开始
        deal = DeaiClientData()
        gps = list(self.db1.price_list.keys())

        all_data = []
        for i in range(0, len(gps), 80):
            sub_codes_list = gps[i:i + 80]
            zh_lx = Account.zh_lx
            action = 'get_tick_datas'
            deal = DeaiClientData()
            data = deal.get_tick_datas(action, sub_codes_list, zh_lx)
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error('db_ym1:_update_codes_list_thread:JSON 解析失败', exc_info=True)
                    continue

            if data is not None:
                all_data.extend(data)

        data = all_data

        #zh_lx=Account.zh_lx
       # action = 'get_tick_datas'
       # try:
           # data = deal.get_tick_datas(action, gps,zh_lx)
            #if isinstance(data, str):
                #data = json.loads(data)
       # except Exception as e:
            #logger.error('db1:worker:run:获取实时数据或解析 JSON 时出错', exc_info=True)
           # self.finished.emit()
            #return
        buy_lx="db"
        if data is not None:
            for item in data:
                if self.db1.zxzt_total == 0:
                    self.db1.set_enabled(False)
                    return

                code = item['code']
                price = float(item['close'])

                close_price = self.db1.findp_rice(self.db1.price_list, code)
                if close_price is None:
                    print(f"未找到代码 {code} 的昨日收盘价，跳过处理")
                    continue
                zt_price = self.zt_price(code, close_price)
                try:
                    # 在9点30分剔除掉一字板
                    if "dyzb" not in self.jon:
                        try:
                            zh_lx = Account.zh_lx
                            action = "get_tick_data"
                            dyzbdata = deal.get_tick_data(action, code, zh_lx)
                            dyzbdata = json.loads(dyzbdata)
                            if float(dyzbdata["open"])==zt_price:

                                with self.db1.strategy_lock:

                                    self.db1.price_list.pop(code, None)
                                    code=None

                                    if self.db1.price_list is None or len(self.db1.price_list) == 0:
                                        self.db1.set_enabled(False)
                                        return
                        except Exception as e:
                            logger.error('db1:worker:get_tick_data:dyzbdata：获取实时数据或解析 JSON 时出错', exc_info=True)
                            self.finished.emit()
                            return


                    if code:
                        # 涨停炸板再次封板时买入
                        if "buy_condition" in self.jon:
                            if self.jon["buy_condition"] == "涨停炸板再次封板时买入":
                                try:
                                    zh_lx = Account.zh_lx
                                    action = "get_tick_data"
                                    co = deal.get_tick_data(action, code,zh_lx)
                                    co = json.loads(co)
                                except Exception as e:
                                    logger.error('db1:worker:get_tick_data:获取实时数据或解析 JSON 时出错', exc_info=True)
                                    self.finished.emit()
                                    return
                                with self.db1.strategy_lock:
                                    if co["high"] == zt_price and price < zt_price:
                                        if code not in self.zt_gps:
                                            self.zt_gps.append(code)
                                    for gp in self.zt_gps[:]:
                                        zb_data = deal.get_tick_data(action, gp,zh_lx)
                                        zb = json.loads(zb_data)
                                        zb_code = zb['code']
                                        zb_price = float(zb['close'])
                                        close_price = self.db1.findp_rice(self.db1.price_list, zb_code)
                                        zt_price = self.zt_price(zb_code, close_price)
                                        if zb_price == zt_price:
                                            self.zt_gps.remove(zb_code)
                                            self.trading_handler.handle_trading(self.db1, zb_code, zt_price, self,buy_lx)

                        # 触及涨停
                        if "buy_condition" in self.jon:
                            if self.jon["buy_condition"] == "触发涨停价时买入":
                                if zt_price == price:
                                    self.trading_handler.handle_trading(self.db1, code, price, self,buy_lx)
                        # 涨停且卖一无封单
                        if "buy_condition" in self.jon:
                            if self.jon["buy_condition"] == "涨停且卖一无封单时买入":
                                if zt_price == price:
                                    # 卖一的量是0,卖一卖二均无封单
                                    if int(float(item["ask_vol1"])) == 0 and int(float(item["ask_vol2"])) == 0:
                                        self.trading_handler.handle_trading(self.db1, code, price, self,buy_lx)

                            # 剩卖一时买入
                        if "buy_condition" in self.jon:
                            if self.jon["buy_condition"] == "剩卖一时买入":
                                # 只有卖一的量大于0
                                if int(float(item["ask_vol1"])) > 0 and int(float(item["ask_vol2"])) == 0 and int(
                                        float(item["ask_vol3"])) == 0 and int(float(item["ask_vol4"])) == 0:
                                    db_price = self.mc_price(item, close_price, code)
                                    self.trading_handler.handle_trading(self.db1, code, db_price, self,buy_lx)

                        # 剩卖二两档时买入
                        if "buy_condition" in self.jon:
                            if self.jon["buy_condition"] == "剩卖二二档时买入":
                                # 只有卖一的量大于0
                                if int(float(item["ask_vol1"])) > 0 and int(float(item["ask_vol2"])) > 0 and int(
                                        float(item["ask_vol3"])) == 0 and int(float(item["ask_vol4"])) == 0 and int(
                                        float(item["ask_vol5"])) == 0:
                                    db_price = self.mc_price(item, close_price, code)
                                    self.trading_handler.handle_trading(self.db1, code, db_price, self,buy_lx)

                        # 剩卖33档时买入
                        if "buy_condition" in self.jon:
                            if self.jon["buy_condition"] == "剩卖三三档时买入":
                                if int(float(item["ask_vol1"])) > 0 and int(float(item["ask_vol2"])) > 0 and int(
                                        float(item["ask_vol3"])) > 0 and int(float(item["ask_vol4"])) == 0 and int(
                                        float(item["ask_vol5"])) == 0:
                                    db_price = self.mc_price(item, close_price, code)
                                    self.trading_handler.handle_trading(self.db1, code, db_price, self,buy_lx)

                        # 涨停且卖一封单小于X万时买入
                        if "buy_condition" in self.jon:
                            if self.jon["buy_condition"] == "涨停且卖一封单小于X万时买入":
                                if "myfd" in self.jon:
                                    myfd = float(self.jon["myfd"]) * 10000
                                    if zt_price == price:
                                        # 明天检查一下这里是首还是实际的量
                                        if float(item["ask_vol1"]) * price * 100 <= myfd:
                                            db_price = self.mc_price(item, close_price, code)

                                            self.trading_handler.handle_trading(self.db1, code, db_price, self,buy_lx)

                        # 买一封板资金大于X万时买入（卖一无封单）
                        if "buy_condition" in self.jon:
                            if self.jon["buy_condition"] == "买一封板资金大于X万时买入（卖一无封单）":
                                if "buyfbzj" in self.jon:
                                    if zt_price == price:

                                        if int(float(item["ask_vol1"])) == 0:
                                            buyfbzj = float(self.jon["buyfbzj"]) * 10000
                                            if float(item["bid_vol1"]) * price * 100 >= buyfbzj:
                                                self.trading_handler.handle_trading(self.db1, code, zt_price, self,buy_lx)
                    end = time.perf_counter()  # 高精度计时结束
                    duration = end - start
                    print(f"程序运行时间: {duration:.3f} 秒")
                except Exception as e:
                    logger.error('db1:worker:run:买入程序出错', exc_info=True)
                    self.finished.emit()
                    return
        self.finished.emit()


        #找出打一字板的时间
    def find_yzb_time(self):
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        today_total_minutes = current_hour * 60 + current_minute
        dyzb = 565 <= today_total_minutes < 570
        if dyzb:
            return dyzb
        else:
            return False

    def mc_price(self, item, zr_price, gpdm):
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
