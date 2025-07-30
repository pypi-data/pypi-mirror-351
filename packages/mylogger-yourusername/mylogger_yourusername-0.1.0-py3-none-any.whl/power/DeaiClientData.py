from power.Tcpclient import TcpClient
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
    def list_sbmx_data(self,data):

        message = {"action": data}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)

        #print(f"DeaiClientData list_sbmx_data:{respon}")
        return respon

    def list_gp_data(self,data,params):
        message = {"action": data, "params": params}
        tcp = TcpClient()
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def query_like_list_data(self, action, params):
        message = {"action": action, "params": params}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def query_username_power(self,action, wechat, qq, code):
        message = {"action": action, "wechat": wechat,"qq":qq,"acc":code}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon
    def add_wechat(self,action,wechat,id):

        message = {"action": action, "wechat": wechat, "id": id}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon
    def add_qq(self,action,qq,id):
        message = {"action": action, "qq": qq, "id": id}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def add_acc(self, action, acc, id):
        message = {"action": action, "acc": acc, "id": id}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def add_zh_lx(self, action, zh_lx, id):
        message = {"action": action, "zh_lx": zh_lx, "id": id}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def add_rq(self, action, start_rq,end_rq, id):
        message = {"action": action, "start_rq": start_rq,"end_rq":end_rq, "id": id}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon
