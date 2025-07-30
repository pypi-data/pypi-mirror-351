from datetime import datetime, timedelta
from ast import literal_eval
from santou.DeaiClientData import DeaiClientData
import pandas as pd

# 全局变量缓存节假日数据和最后一次查询的日期
china_holidays_cache = None
last_query_date = None
china_holidays =None

#这个要在main中就要提前加载
class ChinaHolidays:
    def __init__(self):
        global china_holidays
        self.china_holidays = self._load_holidays()
        #print(self.china_holidays)

    def __new__(cls):
        """实现单例模式"""
        if not hasattr(cls, '_instance'):
            cls._instance = super(ChinaHolidays, cls).__new__(cls)
        return cls._instance



    def _load_holidays(self):
        """加载中国节假日数据，每天只查询一次"""
        global china_holidays_cache, last_query_date

        today = datetime.now().date()

        # 如果缓存为空或日期已变化，则重新查询
        if china_holidays_cache is None or last_query_date != today:
            current_year = datetime.now().year
            deal = DeaiClientData()
            china_holiday = deal.query_holiday("query_holiday", current_year)
            data_list = literal_eval(china_holiday)  # 安全地解析字符串
            china_holidays_cache = pd.to_datetime(data_list).date  # 转换为日期格式
            last_query_date = today  # 更新最后一次查询的日期

        return china_holidays_cache

    def find_stock_trading_time_by_date(self, date):
        """判断是否是交易日"""
        # 判断是否是法定节假日
        if date in self.china_holidays:
            return True

        # 判断是否是周末
        if date.weekday() >= 5:  # 周六是 5，周日是 6
            return True

        # False 表示交易日
        return False

    def is_china_stock_trading_time(self):
        """判断是否是交易日"""
        # 加载节假日数据


        now = datetime.now()
        today = now.date()

        # 判断是否是法定节假日
        if today in self.china_holidays:
            return True

        # 判断是否是周末
        if today.weekday() >= 5:  # 周六是 5，周日是 6
            return True

        # False 表示交易日
        return False
    #d对交易时间段进行检查
    def is_china_stock_trading_time_d(self):
        """判断是否是交易日"""
        # 加载节假日数据

        now = datetime.now()
        today = now.date()

        # 判断是否是法定节假日
        if today in self.china_holidays:
            return False
        # 判断是否是周末
        if today.weekday() >= 5:  # 周六是 5，周日是 6
            return False
        # 判断是否在交易时间内
        current_time = now.time()
        morning_start = datetime.strptime("09:15", "%H:%M").time()
        morning_end = datetime.strptime("11:30", "%H:%M").time()
        afternoon_start = datetime.strptime("13:00", "%H:%M").time()
        afternoon_end = datetime.strptime("15:00", "%H:%M").time()

        if (morning_start <= current_time <= morning_end) or (afternoon_start <= current_time <= afternoon_end):
            return True

        return False

    # 往前找出两个交易日
    def find_two_jyr(self):
        """从今天开始往前找两个交易日，如果今天是交易日则包含今天"""
        trading_days = []  # 用于存储找到的交易日
        current_date = datetime.now().date()  # 获取当前日期

        # 如果今天是交易日，则包含今天
        if not self.find_stock_trading_time_by_date(current_date):
            trading_days.append(current_date)

        # 继续往前找，直到找到两个交易日
        while len(trading_days) < 2:
            current_date -= timedelta(days=1)  # 日期减一天
            if not self.find_stock_trading_time_by_date(current_date):
                trading_days.append(current_date)

        # 返回结果，按时间顺序排列（从早到晚）
        return sorted(trading_days)

    def is_between_1130_and_1300_on_trading_day(self):
        """判断当前时间是否在交易日的11:30到13:00之间"""
        now = datetime.now()
        today = now.date()
        # 判断是否是交易日
        if self.find_stock_trading_time_by_date(today):
            return False
        # 判断时间是否在11:30到13:00之间
        current_time = now.time()
        start_time = datetime.strptime("11:30", "%H:%M").time()
        end_time = datetime.strptime("13:00", "%H:%M").time()

        return start_time <= current_time <= end_time

        # 不在交易时间内，用于不在交易时间更新

    def is_trading_time(self):

        now = datetime.now()
        today = now.date()
        # 判断是否在交易时间内
        current_time = now.time()
        morning_start = datetime.strptime("09:15", "%H:%M").time()
        afternoon_end = datetime.strptime("15:00", "%H:%M").time()

        if (morning_start <= current_time <= afternoon_end) and (today not in self.china_holidays) and (
                today.weekday() < 5):
            return True

        return False