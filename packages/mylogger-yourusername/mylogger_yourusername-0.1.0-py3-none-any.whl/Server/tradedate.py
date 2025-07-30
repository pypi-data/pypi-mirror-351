import pandas as pd
from datetime import datetime, time
from Holiday import Holiday
import json
def is_china_stock_trading_time():
    # 获取当前日期和时间

    now = datetime.now()
    # 获取今年年份
    current_year = datetime.now().year
    today = now.date()
    current_time = now.time()

    holiday=Holiday()
    china_holiday=holiday.queryholiday(current_year)
    data_list = eval(china_holiday)  # 或者使用 ast.literal_eval(data) 更加安全
    # 将假期列表转换为日期格式
    china_holidays = pd.to_datetime(data_list).date
    #print(f"today: {today in china_holidays}")
    # 判断是否是法定节假日
    if today in china_holidays:
        return False

    # 判断是否是周末
    if today.weekday() >= 5:  # 周六是 5，周日是 6
        return False

    # 判断是否在交易时间
    morning_start = time(9, 15)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)


    if(current_time<morning_start or morning_end<current_time<afternoon_start or current_time>afternoon_end):
        return False

    return True


# 示例：判断当前时间是否是交易时间
if is_china_stock_trading_time():
    print(f"现在是中国股市交易时间")
else:
    print(f"现在不是中国股市交易时间")
