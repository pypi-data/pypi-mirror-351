import pymysql
from datetime import datetime, time
from datetime import datetime, timedelta
from ConMysql import mysqlconnsingle
import jsppy.jsp as jsp
from jsp import jspSJ
import json
from Server.log import logger
from trading_time import ChinaHolidays
from DealServerData import DealServerData

def convert_to_yi(num):
    num_in_yi = num / 1e8  # 转换为亿
    return f"{num_in_yi:.1f}"  # 保留1位小数
def cheacktime():
    # 获取当前时间
    now = datetime.now().time()

    # 定义下午三点的时间
    target_time = time(15, 0)  # 15:00:00

    # 判断当前时间是否在下午三点之前
    if now < target_time:
        return True
    else:
        return False





def checkholiday():
    now = datetime.now()
    ho=ChinaHolidays()

    #交易时间不能更新
    #if ho.is_trading_time():
        #print("是交易时间")
       # return
    #交易时间之外开始更新
    date_list=ho.find_jyr()
    # 定义目标格式
    target_format = "%Y-%m-%d"
    li = [date.strftime(target_format) for date in date_list]

    #找出最近的两个交易日
    today=li[1]
    yestoday = li[0]


    sql = """
               select id,gxrq from gxrq
          """
    co = mysqlconnsingle()
    conn=co.conn()
    data1=co.query_one_sql(sql)

    if data1 is None:
        DealServerData().save_gxrq(yestoday)

    if data1['gxrq']!=today:
        DealServerData().update_gxrq(data1['id'],today)

        #说明没有更新，开始更新today
        sql = """
                select gpdm,ltgbnum,zgbnum,xj,vol,ztzt from wcdata
              """
        data = co.query_sql(sql, params=None)

        API = jsp.Init_jsp()
        js=jspSJ()
        try:
            rq2 = now.date()
            rq1 = now.date() - timedelta(days=25)
            for row in data:
                gpdm = row['gpdm']
                ltgbnum = row['ltgbnum']
                zgbnum = row['zgbnum']
                ztzt = row['ztzt']

                if ho.is_china_stock_trading_time_d():
                    ztzt=ztzt
                else:
                    m = js.getztbnum(API, js, str(rq1), str(rq2), gpdm)
                    ztzt=str(m)
                #获取在25天内的涨停数量
                jon_yestody = json.loads(str(js.getrxsj(gpdm, str(yestoday), jsp, API)))
                jon=json.loads(str(js.getrxsj(gpdm,str(today),jsp,API)))
                #两个必须同时不能为空，否则有个数据没查出来导致为空
                if  jon and jon_yestody:
                   # print(jon)
                    table_name = "wcdata"
                    condition = f"gpdm = {gpdm}"

                    update_data = {
                        "xj":str(jon['close']),
                        "openj": str(jon['open']),
                        "highj": str(jon['high']),
                        "lowj": str(jon['low']),
                        "gxrq": str(today),
                        "ltsz": convert_to_yi(float(ltgbnum)*float(jon['close'])),
                        "zsz": convert_to_yi(float(zgbnum) * float(jon['close'])),
                        "ztzt": ztzt,
                        "vol": str(jon['vol']),
                        #上一天的收盘价
                        "close_pre_day_price":str(jon_yestody['close'])
                    }
                    #更新数据
                    fields = ", ".join([f"{key} = %s" for key in update_data.keys()])
                    sql = f"UPDATE {table_name} SET {fields} WHERE {condition}"
                    co.update_wcdata(conn,sql,update_data)
                   # 更新涨停板数量
            jsp.destroy_jsp(API)
        except pymysql.MySQLError as e:
            logger.error('timetask:checkholiday:更新操作失败', exc_info=True)
            conn.rollback()  # 回滚事务
        finally:
            if conn:
                conn.commit()
                conn.close()
         #用完关连接
        jsp.destroy_jsp(API)




class TimeTsk():
    def __init__(self):
        super(TimeTsk, self).__init__()
    def timetask(self):
        checkholiday()  # 立即执行第一次









