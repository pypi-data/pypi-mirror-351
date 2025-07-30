import jsppy.jsp as jsp

import pandas as pd
import json
import numpy as np
import time
from datetime import datetime, timedelta  # 明确导入 datetime 和 timedelta
# 转换函数，用于将 numpy 数据类型转换为原生 Python 数据类型
from Server.log import logger

# 自定义 numpy 数据类型转换函数
def numpy_converter(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

class jspSJ():
    def __init__(self):
        super(jspSJ, self).__init__()

    #获取一个时间段一分钟
    def getrxsj_by_one_min(self, code, rq, jsp, API):
        pd.set_option('display.max_columns', None)  # 显示所有列
        pd.set_option('display.max_rows', None)  # 显示所有行
        pd.set_option('display.width', None)  # 自动调整宽度
        pd.set_option('display.max_colwidth', None)  # 显示完整列内容
        df = jsp.get_recent_data(API, code, rq, rq, "1min")

        try:
            now = datetime.now()
            # 计算前一分钟
            previous_minute = now - timedelta(minutes=1)
            # 格式化为目标字符串
            pre_time = previous_minute.strftime("%Y-%m-%d %H:%M")
            df1 = df[df["datetime"] == pre_time]

            target_time = str(now.strftime("%Y-%m-%d %H:%M"))
            df2 = df[df["datetime"] == target_time]
            jon = {}
            if not df1.empty and not df2.empty:
                #jon["code"] = df["code"].iloc[0]
                #jon["open"] = df["open"].iloc[0]
                #jon["high"] = df["high"].iloc[0]
                #jon["low"] = df["low"].iloc[0]
                jon["close1"] = str(df1["close"].iloc[0])
                jon["close2"] = str(df2["close"].iloc[0])
                #jon["vol"] = df["vol"].iloc[0]
                #jon = json.dumps(jon, default=numpy_converter, indent=4)
                print(jon)
            return jon
        except Exception as e:
            logger.error('jsp:getrxsj_by_one_min:发生错误', exc_info=True)
            jsp.destroy_jsp(API)
            time.sleep(3)

    def getrxsj(self,code,rq,jsp,API):
        pd.set_option('display.max_columns', None)  # 显示所有列
        pd.set_option('display.max_rows', None)  # 显示所有行
        pd.set_option('display.width', None)  # 自动调整宽度
        pd.set_option('display.max_colwidth', None)  # 显示完整列内容
        try:
            df=jsp.get_recent_data(API,code,rq,rq,"D")
            jon={}
            if df.empty==False:
                jon["code"] = df["code"].iloc[0]
                jon["open"]=df["open"].iloc[0]
                jon["high"]=df["high"].iloc[0]
                jon["low"]=df["low"].iloc[0]
                jon["close"] = df["close"].iloc[0]
                jon["vol"] = df["vol"].iloc[0]
                jon = json.dumps(jon, default=numpy_converter, indent=4)

            return jon
        except Exception as e:
            logger.error('jsp:getrxsj:发生错误', exc_info=True)
            jsp.destroy_jsp(API)
            time.sleep(1)


        # 判断是否涨停板，以及几个涨停
    def getztbnum(self, API, js, rq1, rq2,gpdm):
        pd.set_option('display.max_columns', None)  # 显示所有列
        pd.set_option('display.max_rows', None)  # 显示所有行
        pd.set_option('display.width', None)  # 自动调整宽度
        pd.set_option('display.max_colwidth', None)  # 显示完整列内容
        df = jsp.get_recent_data(API, gpdm, rq1, rq2, "D")
        try:
            m = 0
            for i in range(len(df)-1, -1, -1):
                # 获取收盘值
                if i - 1 != -1:
                    value1 = df.iloc[i, 1]
                    value2 = df.iloc[i - 1, 1]
                    if gpdm.startswith("30") or gpdm.startswith("688"):
                        if float(value1) == round(float(value2) * 1.2, 2):
                            m = m + 1
                        else:
                            break

                    if gpdm.startswith("00") or gpdm.startswith("60"):
                        if float(value1) == round(float(value2) * 1.1, 2):
                            m = m + 1
                        else:
                            break

                    if gpdm.startswith("8"):
                        if float(value1) == round(float(value2) * 1.3, 2):
                            m = m + 1
                        else:
                            break
            #print(f"m: {m}")
            return m
        except Exception as e:
            logger.error('jsp:getrxsj:发生错误', exc_info=True)
            jsp.destroy_jsp(API)
            time.sleep(1)
#now = datetime.now()
#rq1 = now.date()
#rq2 = now.date() - timedelta(days=25)
#print(rq2)


    #获取单个股票实时数据
    def get_jsp_tickdata(self,code):

        # 设置 Pandas 显示选项
        pd.set_option('display.max_columns', None)  # 显示所有列
        pd.set_option('display.max_rows', None)  # 显示所有行
        pd.set_option('display.width', None)  # 自动调整宽度
        pd.set_option('display.max_colwidth', None)  # 显示完整列内容
        jon = {}
        API = jsp.Init_jsp()
        try:
            df=jsp.get_real_hq(API,[code])


            if df.empty == False:
                jon["close"] = df["price"].iloc[0]
                jon["code"] = df["code"].iloc[0]
                jon['vol'] = df['vol'].iloc[0]
                jon['amount'] = df['amount'].iloc[0]
                jon['s_vol'] = df['s_vol'].iloc[0]
                jon['b_vol'] = df['b_vol'].iloc[0]
                jon["bid1"] = df["bid1"].iloc[0]
                jon["ask1"] = df["ask1"].iloc[0]
                jon["bid2"] = df["bid2"].iloc[0]
                jon["ask2"] = df["ask2"].iloc[0]
                jon["bid3"] = df["bid3"].iloc[0]
                jon["ask3"] = df["ask3"].iloc[0]
                jon["bid4"] = df["bid4"].iloc[0]
                jon["ask4"] = df["ask4"].iloc[0]
                jon["bid5"] = df["bid5"].iloc[0]
                jon["ask5"] = df["ask5"].iloc[0]

                jon["bid_vol1"] = df["bid_vol1"].iloc[0]
                jon["ask_vol1"] = df["ask_vol1"].iloc[0]
                jon["bid_vol2"] = df["bid_vol2"].iloc[0]
                jon["ask_vol2"] = df["ask_vol2"].iloc[0]
                jon["bid_vol3"] = df["bid_vol3"].iloc[0]
                jon["ask_vol3"] = df["ask_vol3"].iloc[0]
                jon["bid_vol4"] = df["bid_vol4"].iloc[0]
                jon["ask_vol4"] = df["ask_vol4"].iloc[0]
                jon["bid_vol5"] = df["bid_vol5"].iloc[0]
                jon["ask_vol5"] = df["ask_vol5"].iloc[0]
                jon = json.dumps(jon, default=numpy_converter, indent=4)
                jsp.destroy_jsp(API)
                return jon
        except Exception as e:
            logger.error('jsp:get_jsp_tickdata:发生错误', exc_info=True)
            jsp.destroy_jsp(API)
            time.sleep(1)

    def get_jsp_tickdatas(self,codes):
        # 设置 Pandas 显示选项
        pd.set_option('display.max_columns', None)  # 显示所有列
        pd.set_option('display.width', None)  # 自动调整宽度

        pd.set_option('display.max_rows', None)  # 显示所有行
        pd.set_option('display.max_colwidth', None)  # 显示完整列内容
        jon =[]
        API = jsp.Init_jsp()
        try:
            df=jsp.get_real_hq(API,codes)
            print(df)
            if df.empty == False:
                for index, row in df.iterrows():
                    ro={}
                    ro['code']=str(row['code'])
                    ro['close'] = str(row['price'])
                    ro['servertime'] = row['servertime']
                    ro['bid1']=str(row['bid1'])
                    ro['ask1'] = str(row['ask1'])
                    ro['bid2'] = str(row['bid2'])
                    ro['ask2'] = str(row['ask2'])
                    ro['bid3'] = str(row['bid3'])
                    ro['ask3'] = str(row['ask3'])
                    ro['bid4'] = str(row['bid4'])
                    ro['ask4'] = str(row['ask4'])
                    ro['bid5'] = str(row['bid5'])
                    ro['ask5'] = str(row['ask5'])
                    ro['vol'] = str(row['vol'])
                    ro['amount'] = str(row['amount'])
                    ro['s_vol'] = str(row['s_vol'])
                    ro['b_vol'] = str(row['b_vol'])
                    ro['bid_vol1'] = str(row['bid_vol1'])
                    ro['ask_vol1'] = str(row['ask_vol1'])
                    ro['bid_vol2'] = str(row['bid_vol2'])
                    ro['ask_vol2'] = str(row['ask_vol2'])
                    ro['bid_vol3'] = str(row['bid_vol3'])
                    ro['ask_vol3'] = str(row['ask_vol3'])
                    ro['bid_vol4'] = str(row['bid_vol4'])
                    ro['ask_vol4'] = str(row['ask_vol4'])
                    ro['bid_vol5'] = str(row['bid_vol5'])
                    ro['ask_vol5'] = str(row['ask_vol5'])
                    jon.append(ro)
                jon = json.dumps(jon, default=numpy_converter, indent=4)
                #print(jon)
                jsp.destroy_jsp(API)
                return jon
        except Exception as e:
            logger.error('jsp:get_jsp_tickdatas:发生错误', exc_info=True)
            jsp.destroy_jsp(API)
            time.sleep(1)

    def get_code_tick(self,API,code):
        # 设置 Pandas 显示选项
        pd.set_option('display.max_columns', None)  # 显示所有列
        pd.set_option('display.width', None)  # 自动调整宽度
        pd.set_option('display.max_rows', None)  # 显示所有行
        pd.set_option('display.max_colwidth', None)  # 显示完整列内容
        now = datetime.now()
        rq = now.strftime("%Y-%m-%d")
        print(rq)
        jon =[]
        API = jsp.Init_jsp()
        try:
            df=jsp.get_tick(API,code,"2025-03-25")

            print(df)
            if df.empty == False:
                for index, row in df.iterrows():
                    ro={}
                    ro['code']=str(row['code'])
                    ro['close'] = str(row['price'])
                    ro['servertime'] = row['servertime']

                    ro['bid1']=str(row['bid1'])
                    ro['ask1'] = str(row['ask1'])
                    ro['bid2'] = str(row['bid2'])
                    ro['ask2'] = str(row['ask2'])
                    ro['bid3'] = str(row['bid3'])
                    ro['ask3'] = str(row['ask3'])
                    ro['bid4'] = str(row['bid4'])
                    ro['ask4'] = str(row['ask4'])
                    ro['bid5'] = str(row['bid5'])
                    ro['ask5'] = str(row['ask5'])
                    ro['vol'] = str(row['vol'])
                    ro['amount'] = str(row['amount'])
                    ro['s_vol'] = str(row['s_vol'])
                    ro['b_vol'] = str(row['b_vol'])
                    ro['bid_vol1'] = str(row['bid_vol1'])
                    ro['ask_vol1'] = str(row['ask_vol1'])
                    ro['bid_vol2'] = str(row['bid_vol2'])
                    ro['ask_vol2'] = str(row['ask_vol2'])
                    ro['bid_vol3'] = str(row['bid_vol3'])
                    ro['ask_vol3'] = str(row['ask_vol3'])
                    ro['bid_vol4'] = str(row['bid_vol4'])
                    ro['ask_vol4'] = str(row['ask_vol4'])
                    ro['bid_vol5'] = str(row['bid_vol5'])
                    ro['ask_vol5'] = str(row['ask_vol5'])
                    jon.append(ro)
                jon = json.dumps(jon, default=numpy_converter, indent=4)
                #print(jon)
                jsp.destroy_jsp(API)
                return jon
        except Exception as e:
            logger.error('jsp:get_jsp_tickdatas:发生错误', exc_info=True)
            jsp.destroy_jsp(API)
            time.sleep(1)

#API = jsp.Init_jsp()
#js = jspSJ()
#js.get_jsp_tickdatas(['002981'])
#jsp.destroy_jsp(API)

#API = jsp.Init_jsp()
#js = jspSJ()
#js.get_code_tick(API,'SZ.002981')
#jsp.destroy_jsp(API)


#API = jsp.Init_jsp()
#js = jspSJ()
#js.getztbnum(API, js, "2025-03-05", "2025-03-05",'002981')
#
#API = jsp.Init_jsp()
#js = jspSJ()
#js.getrxsj_by_one_minute("002981","2025-03-14",jsp,API)
#jsp.destroy_jsp(API)

API = jsp.Init_jsp()
js = jspSJ()
js.getrxsj("002981","2025-04-15",jsp,API)
jsp.destroy_jsp(API)






