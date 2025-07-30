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
    def query_like_list_gp(self, action, params):
        message = {"action": action, "params": params}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def check_stock(self, action, params):
        message = {"action": action, "params": params}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def get_buy_amount_settings(self, action, params):
        message = {"action": action, "params": params}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def save_buy_amount_settings(self, action, params):
        message = {"action": action, "params": params}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon
    def save_cele_set_client(self, action, params,str,rq):
        message = {"action": action, "cele": params, "celesm": str,"rq":rq}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def list_cele_data_client(self, action, params):
        message = {"action": action, "cele": params}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon
    #寻找交易日
    def query_holiday(self, action, params):
        message = {"action": action, "params": params}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def save_db_data(self,action, jon,rq,username,gps,dblx):
        message = {"action": action, "cele": jon, "rq": rq, "username": username,"list":gps,"dblx":dblx}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def update_gps(self,action,gps):
        message = {"action": action, "gps": gps}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)

        return respon

    def query_sbzt_by_id(self,action,id):
        message = {"action": action, "id":id}
        # 给发送端
        #print(f"m: {message}")
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def gettickdata(self,gpdm):
        message = {"action": "gettickdata", "params":gpdm}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon
    #获取账户数据
    def get_account_data(self,action,username):
        message = {"action": action,"username":username}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def delete_account_data(self,action,id):
        message = {"action": action,"id":id}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def save_qmt_addr_zh_data(self,action,params):
        message = {"action": action,"params":params}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def set_default_account(self,action,id,username):
        message = {"action": action,"id":id,"username":username}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def get_dz_zh_settings(self, action, params):
        message = {"action": action, "params": params}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def get_tick_datas(self, action, params,zh_lx):
        message = {"action": action, "params": params,"zh_lx":zh_lx}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def get_tick_data(self, action, params,zh_lx):
        message = {"action": action, "params": params,"zh_lx":zh_lx}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def getrxsj_by_one_min(self, action, gpdm,zh_lx):
        message = {"action": action, "gpdm": gpdm,"zh_lx":zh_lx}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def load_username_account_data(self,action,username):
        message = {"action": action, "username": username}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def save_cj_data(self,action,params,username,cj_status,czlx):
        date_time=self.get_current_datetime_parts()
        params["date_time"]=date_time
        message = {"action": action, "cj_nr": params,"username":username,"date_time":date_time,"cj_status":cj_status,"czlx":czlx}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def get_current_datetime_parts(self):
        now = datetime.now()
        # 格式化日期为 2025-02-23 这种形式
        rq = now.strftime("%Y-%m-%d %H:%M:%S")
        return rq

    def list_check_gp_data(self,data,params):
        message = {"action": data, "params": params}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def load_db1_data(self,action,username,dblx):
        message = {"action": action, "username": username,"dblx":dblx}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def load_cj_data(self,action,username,rq,czlx):
        message = {"action": action, "username": username,"rq":rq,"czlx":czlx}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def load_sell_data(self,action,username,rq):
        message = {"action": action, "username": username,"rq":rq}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def get_gpmc_by_gpdm(self,action,params):
        message = {"action": action, "params": params}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def update_sell_position(self,action,username,mcsz):
        message = {"action": action, "username": username,"mcsz":mcsz}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def get_mcsz_by_username(self,action,username):
        message = {"action": action, "username": username}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def get_gp_close_datas(self,action,codes_list):
        message = {"action": action, "codes_list": codes_list}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def get_rencent_datas(self,action,codes_list):
        message = {"action": action, "params": codes_list}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def yz_account(self,action,acc):
        message = {"action": action, "acc": acc}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon


    def save_register_zh(self,action,acc,qq,wechat):
        message = {"action": action, "acc": acc,"qq":qq,"wechat":wechat}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def check_duplicate_zh(self,action,acc,qq,wechat):
        message = {"action": action, "acc": acc,"qq":qq,"wechat":wechat}
        # 给发送端
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def add_qq(self,action,qq,id):
        message = {"action": action, "qq": qq, "id": id}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def add_wechat(self, action, acc, id):
        message = {"action": action, "wechat": acc, "id": id}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon

    def get_code_tick(self, action, acc, id):
        message = {"action": action, "wechat": acc, "id": id}
        tcp = TcpClient()
        respon = tcp.start_client(message)
        return respon
