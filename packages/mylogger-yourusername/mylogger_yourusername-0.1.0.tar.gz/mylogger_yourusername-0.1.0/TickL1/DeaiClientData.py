from santou.Tcpclient import TcpClient
import json
from datetime import datetime,date
class DeaiClientData:
    def __init__(self):
        super(DeaiClientData, self).__init__()

    #封装首版主题数据
    def Composite_sbmx_Data(self,action,topic_name, description):
        # 获取当前时间
        now = datetime.now()
        # 提取年月日时分
        year = now.year  # 年
        month = now.month  # 月
        day = now.day  # 日
        hour = now.hour  # 时
        minute = now.minute  # 分
        formatted_time = now.strftime("%Y-%m-%d %H:%M")
        message={"action":action,"zt":topic_name,"xxmx":description,"date":formatted_time}
        #json_str = json.dumps(message, ensure_ascii=False, indent=4)

        #给发送端
        tcp=TcpClient()
        respon=tcp.start_client(message)
        #print(f"respon:{respon}")
        return respon


    #获取5档数据
    def get_tick_datas(self, action, params):
        message = {"action": "get_tick_datas", "params": params, "zh_lx": "3s"}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon
