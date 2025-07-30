import pymysql
from Server.ConMysql import mysqlconnsingle
import uuid
import json
from Server.jsp import jspSJ
import jsppy.jsp as jsp
import ast
from datetime import datetime
from Server.log import logger
#接受服务器数据分发
class DealServerData:
    def __init__(self):
        super(DealServerData, self).__init__()
    def deal_server_data(self, data):
        # 将字符串转换为 JSON 对象

        json_data = data
        action = json_data['action']

        # 动态调用方法
        try:
            method = getattr(self, action)  # 获取对应的方法
            message = method(json_data)         # 调用方法

            return message
        except AttributeError:
            logger.error('DealServerData:deal_server_data:未知的 action', exc_info=True)

            return "未知的 action"


    def getuuid(self):
        uuid_32 = uuid.uuid4().hex
        return uuid_32

    def save_gxrq(self, gxrq):
        try:
            sql = "insert into gxrq(id,gxrq) values (%s,%s)"
            id = self.getuuid()

            conn = mysqlconnsingle()
            message = conn.insert_sql(sql, (id, gxrq))

            return message
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:save_gxrq发生异常', exc_info=True)

    def update_gxrq(self,id, gxrq):
        try:
            sql =  """ UPDATE gxrq  SET gxrq =%s WHERE id = %s"""
            conn = mysqlconnsingle()
            message = conn.insert_sql(sql, (gxrq,id))

            return message
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:update_gxrq发生异常', exc_info=True)



    def deal_sbmx_data(self,data):
        try:
            sql = "insert into sbzt(id,zt,xxmx,date) values (%s,%s,%s,%s)"
            id = self.getuuid()
            zt = data['未执行']
            xxmx = data['xxmx']
            date =data['date']
            conn = mysqlconnsingle()
            message = conn.insert_sql(sql,(id, zt, xxmx,date))
            return message
        except Exception as e:  # 捕获所有其他异常

            logger.error('DealServerData:deal_sbmx_data发生异常', exc_info=True)

    def list_sbmx_data(self,data):
        try:
            str = "select id,zt,cele,date,celesm,list from sbzt order by date desc"
            conn = mysqlconnsingle()
            result = conn.query_sql(str,params=None)
            #print(f"query:{result}")
            return result
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:list_sbmx_data发生异常', exc_info=True)



    def list_gp_data(self, data):
        try:
            params = data['params']

            conn = mysqlconnsingle()
            # 使用 ast.literal_eval() 解析字符串为列表
            if type(params)!=list:
                params = ast.literal_eval(params)

            # 构建 SQL 查询语句，使用占位符 %s 来避免 SQL 注入
            query = f"SELECT id,gpdm,gpmc,xj,ltsz,ztzt,zsz,ltgbnum,openj,xj,close_pre_day_price,vol FROM wcdata WHERE gpdm IN ({','.join(['%s'] * len(params))})"
            mysql = mysqlconnsingle()
            # 执行查询，确保传递的参数和占位符数量一致
            params = tuple(params)
            result = mysql.query_sql(query, params)
            return result
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:list_gp_data发生异常', exc_info=True)


    def list_check_gp_data(self, data):
        try:

            params=data['params']
            str = f"SELECT gpdm,xj,ltsz,ltgbnum FROM wcdata WHERE gpdm IN ({','.join(['%s'] * len(params))})"
            mysql = mysqlconnsingle()
            result = mysql.query_sql(str, params)
            return result
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:list_check_gp_data发生异常', exc_info=True)

    @staticmethod
    def list_all_gpdm_data():
        try:
            str = "select gpdm,ztzt from wcdata "
            mysql = mysqlconnsingle()
            result = mysql.query_sql(str, params=None)
            #print(f"query:{result}")

            return result
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:list_all_gpdm_data发生异常', exc_info=True)
    def like_query_ck(self,data):
        try:
            params = data['params']
            co=mysqlconnsingle()
            conn = co.conn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # 定义搜索关键字
            search_keyword = f'%{params}%'
            # 执行多字段 LIKE 查询
            sql = "SELECT DISTINCT gn FROM gngp WHERE gn LIKE %s"  # 使用 DISTINCT 去重

            cursor.execute(sql,(search_keyword,))
            data = cursor.fetchall()  # 返回一个字典形式的结果列表
            if data:
                #print("JSON 格式查询结果：", data)
                return data
            else:
                print("未取到值")

            conn.close()
            return data
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:like_query_ck发生异常', exc_info=True)

    def like_query_gp_list(self,data):
        try:
            params = data['params']

            co=mysqlconnsingle()
            conn = co.conn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # 定义搜索关键字
            search_keyword = f'{params}'
            # 执行多字段 LIKE 查询
            sql = "SELECT DISTINCT gpdm,gpmc,gn FROM gngp WHERE gn = %s"  # 使用 DISTINCT 去重

            cursor.execute(sql,(search_keyword,))
            data = cursor.fetchall()  # 返回一个字典形式的结果列表
            if data:
               # print("JSON 格式查询结果like_query_gp_list：", data)
                return data
            else:
                print("未取到值")

            conn.close()
            return data
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:like_query_gp_list发生异常', exc_info=True)

    def check_stock(self,data):
        try:
            params = data['params']

            co = mysqlconnsingle()
            conn = co.conn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # 定义搜索关键字

            search_keyword = f'%{params}%'

            # 执行多字段 LIKE 查询
            sql = "SELECT DISTINCT gpdm,gpmc FROM wcdata WHERE gpmc like %s or gpdm like %s"  # 使用 DISTINCT 去重
            #print(f"search_keyword: {search_keyword}")
            cursor.execute(sql, (search_keyword,search_keyword))
            data = cursor.fetchall()  # 返回一个字典形式的结果列表
            if data:

                return data
            else:
                print("未取到值")

            conn.close()
            return data
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:check_stock发生异常', exc_info=True)

    def get_buy_amount_settings(self,data):
        try:

            co = mysqlconnsingle()
            conn = co.conn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 执行多字段 LIKE 查询
            sql = "SELECT  id,dbzj,zhtjdzj FROM sz_gpzj"  # 使用 DISTINCT 去重

            cursor.execute(sql)
            data = cursor.fetchall()  # 返回一个字典形式的结果列表

            if data:
                #print("JSON 格式查询结果like_query_gp_list：", data)
                return data
            else:
                print("未取到值")

            conn.close()
            return data
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:get_buy_amount_settings', exc_info=True)

    def save_buy_amount_settings(self,data):
        try:
            id = data['params']['id'].strip()
            if id:
                sql = """
                       UPDATE sz_gpzj
                       SET dbzj =%s,zhtjdzj=%s
                       WHERE id = %s
                       """
                dbzj = data['params']['dbzj']
                zhtjdzj = data['params']['zhtjdzj']
                conn = mysqlconnsingle()
                message = conn.insert_sql(sql, ( dbzj, zhtjdzj,id))
                return message
            else:
                sql = "insert into sz_gpzj(id,username,dbzj,zhtjdzj) values (%s,%s,%s,%s)"

                #username = data['username']
                username="ding"
                id = self.getuuid()
                dbzj = data['params']['dbzj']
                zhtjdzj =data['params']['zhtjdzj']
                conn = mysqlconnsingle()
                message = conn.insert_sql(sql,(id, username, dbzj,zhtjdzj))
                #print(f"me: {message}")
                return message
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:save_buy_amount_settings发生异常', exc_info=True)


    def save_cele_set_server(self,data):
        try:
                sql = "insert into db_cele(id,cele,username,celesm,rq) values (%s,%s,%s,%s,%s)"
                #username = data['username']
                username="ding"
                id = self.getuuid()
                cele = data['cele']
                celesm = data['celesm']
                rq = data['rq']
                conn = mysqlconnsingle()
                message = conn.insert_sql(sql,(id,cele,username,celesm,rq))
                #print(f"me: {message}")
                return message
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:save_cele_set_server', exc_info=True)
    def list_cele_data_server(self,data):
        try:
            co = mysqlconnsingle()
            conn = co.conn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # 执行多字段 LIKE 查询
            sql = "SELECT  id,cele,mrzt,celesm,rq FROM db_cele"  # 使用 DISTINCT 去重

            cursor.execute(sql)
            data = cursor.fetchall()  # 返回一个字典形式的结果列表

            if data:
                #print("JSON 格式查询结果like_query_gp_list：", data)
                return data
            else:
                print("未取到值")
            conn.close()
            return data
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:list_cele_data_server', exc_info=True)


    def query_holiday(self,data):
        sql =   """
                   select holiday from holiday where year=%s
                """
        params = (data["params"],)  # 查询参数必须是元组形式
        conn = mysqlconnsingle()
        data=conn.query_sql(sql, params)

        return data[0]["holiday"]

    def query_holiday_server(self,data):
        sql =   """
                   select holiday from holiday where year=%s
                """

        conn = mysqlconnsingle()
        data=conn.query_sql(sql, (data))
        #print(f"type: {type(data[0]['holiday'])}")
        #print(data[0]["holiday"])
        return data[0]["holiday"]

    #保存买入的数据
    def save_db_data(self, data):
        try:

            username = data['username']
            dblx = data['dblx']
            cele = str(data['cele'])
            rq = str(data['rq'])
            gps = str(data['list'])

            # 查询是否存在相关记录
            select_sql = "SELECT id FROM sbzt WHERE username = %s AND dblx = %s"
            conn = mysqlconnsingle()
            result = conn.query_sql(select_sql, (username, dblx))

            if result:
                # 如果存在记录，更新数据
                id = result[0]['id']
                update_sql = "UPDATE sbzt SET cele = %s, date = %s, list = %s WHERE id = %s"
                message = conn.insert_sql(update_sql, (cele, rq, gps, id))
            else:
                # 如果不存在记录，插入数据
                insert_sql = "INSERT INTO sbzt(id, cele, username, date, list, dblx) VALUES (%s, %s, %s, %s, %s, %s)"
                id = self.getuuid()
                message = conn.insert_sql(insert_sql, (id, cele, username, rq, gps, dblx))

            return message
        except Exception as e:
            logger.error('DealServerData:save_db_data发生异常', exc_info=True)


    def load_db1_data(self, data):
        try:

            username = data['username']
            dblx = data['dblx']
            # 查询是否存在相关记录
            select_sql = "SELECT id,cele,list FROM sbzt WHERE username = %s AND dblx = %s"
            conn = mysqlconnsingle()
            result = conn.query_sql(select_sql, (username, dblx))
            return result
        except Exception as e:

            logger.error('DealServerData:load_db1_data发生异常', exc_info=True)


    def update_gps(self, data):
        try:
            gps = data['gps']

            # 如果 gps 是字典，提取其键或值（假设字典的键是股票代码）
            if isinstance(gps, dict):
                gps = list(gps.keys())  # 将字典的键转换为列表
            # 确保 gps 是列表或元组
            if not isinstance(gps, (list, tuple)):
                raise ValueError("gps 参数必须是列表或元组")

            # 构建 SQL 查询
            sql = f"SELECT gpdm, xj FROM wcdata WHERE gpdm IN ({','.join(['%s'] * len(gps))})"
            mysql = mysqlconnsingle()
            result = mysql.query_sql(sql, gps)  # 传递列表或元组作为参数

            return result
        except Exception as e:
            logger.error('DealServerData:update_gps', exc_info=True)


    def query_sbzt_by_id(self,data):
        try:
            id = data['id']
            co = mysqlconnsingle()
            conn = co.conn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # 执行多字段 LIKE 查询
            sql = "SELECT id,list,cele,celesm from sbzt WHERE id = %s"  # 使用 DISTINCT 去重
            cursor.execute(sql, (id,))
            data = cursor.fetchall()  # 返回一个字典形式的结果列表
            if data:
                return data
            else:
                print("未取到值")
            conn.close()
            return data
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:query_sbzt_by_id异常', exc_info=True)

    def gettickdata(self, data):
        gpdm = data['gpdm']
        jsp=jspSJ()
        jon=jsp.gettickdata(gpdm)
        return jon

    def get_account_data(self,data):
        try:
            username = data['username']
            co = mysqlconnsingle()
            conn = co.conn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # 执行多字段 LIKE 查询
            sql = "SELECT id,dz,account,mr_zt from username_account WHERE username = %s"  # 使用 DISTINCT 去重
            cursor.execute(sql, (username,))
            data = cursor.fetchall()  # 返回一个字典形式的结果列表
            if data:
                return data
            else:
                print("未取到值")
            conn.close()
            return data
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:gettickdata异常', exc_info=True)


    def delete_account_data(self, data):
        try:
            # 从 data 中获取 id
            id = data['id']
            # 构建 SQL 删除语句
            sql = "DELETE FROM username_account WHERE id = %s"

            # 获取数据库连接
            conn = mysqlconnsingle()
            # 执行删除操作
            message = conn.insert_sql(sql, (id,))
            # 返回操作结果
            return message
        except Exception as e:
            # 捕获并打印异常
            logger.error('DealServerData:delete_account_data', exc_info=True)
            return None

    def set_default_account(self, data):
        try:
            # 获取参数
            username = data['username']
            id = data['id']
            # 获取数据库连接
            conn = mysqlconnsingle()

            # 第一步：将 username 对应的所有账户的 mr_zt 设置为 "0"
            sql_reset = "UPDATE username_account SET mr_zt = '0' WHERE username = %s"
            conn.insert_sql(sql_reset, (username,))

            # 第二步：将指定 id 的账户的 mr_zt 设置为 "1"
            sql_set_default = "UPDATE username_account SET mr_zt = '1' WHERE id = %s"
            message = conn.insert_sql(sql_set_default, (id,))
            # 返回操作结果
            return {"message": "success"} if message else {"message": "failed"}
        except Exception as e:
            # 捕获并打印异常
            logger.error('DealServerData:set_default_account', exc_info=True)
            return {"message": "failed"}


    def save_qmt_addr_zh_data(self,data):
        try:
            id = data['params']['id'].strip()
            if id:
                sql = """
                              UPDATE username_account
                              SET dz =%s,account=%s
                              WHERE id = %s
                              """
                dz = data['params']['dz']
                account = data['params']['account']
                conn = mysqlconnsingle()
                message = conn.insert_sql(sql, (dz, account, id))
                return message
            else:
                sql = "insert into username_account(id,username,dz,account) values (%s,%s,%s,%s)"

                # username = data['username']

                id = self.getuuid()
                username = data['params']['username']
                dz = data['params']['dz']
                account = data['params']['account']
                conn = mysqlconnsingle()
                message = conn.insert_sql(sql, (id, username, dz, account))
                return message
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:save_qmt_addr_zh_data发生异常', exc_info=True)


    def get_dz_zh_settings(self,data):
        try:
            co = mysqlconnsingle()
            conn = co.conn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 执行多字段 LIKE 查询
            sql = "SELECT  id,dz,account FROM username_account"  # 使用 DISTINCT 去重

            cursor.execute(sql)
            data = cursor.fetchall()  # 返回一个字典形式的结果列表

            if data:
                #print("JSON 格式查询结果like_query_gp_list：", data)
                return data
            else:
                print("未取到值")

            conn.close()
            return data
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:get_dz_zh_settings', exc_info=True)

    def get_tick_datas(self,data):
        try:
            #区分是高速还是低速
            zh_lx = data['zh_lx']

            params=data['params']

            API = jsp.Init_jsp()
            js = jspSJ()
            da=js.get_jsp_tickdatas(params)
            jsp.destroy_jsp(API)
            return da
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:get_tick_datas', exc_info=True)

    # 获取多个股票五档实时数据
    def get_5tick_datas(self,data):
        try:
            params=data['params']
            API = jsp.Init_jsp()
            js = jspSJ()
            da=js.get_jsp_tickdatas(params)
            jsp.destroy_jsp(API)
            return da
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:get_tick_datas', exc_info=True)

    def get_tick_data(self, data):
        try:
            zh_lx = data['zh_lx']
            # 获取今天的日期
            today = datetime.today()
            rq = today.strftime('%Y-%m-%d')
            gpdm = data['params']
            API = jsp.Init_jsp()
            js = jspSJ()
            da = js.getrxsj(gpdm,rq,jsp,API)

            jsp.destroy_jsp(API)
            return da
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:get_tick_datas', exc_info=True)





    def load_username_account_data(self, data):
        try:
            # 获取参数
            username = data['username']

            # 获取数据库连接
            co = mysqlconnsingle()
            conn = co.conn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 执行查询
            sql = "SELECT id, dz, account, mr_zt FROM username_account WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchall()  # 返回一个字典形式的结果列表

            # 关闭连接
            conn.close()

            # 返回查询结果
            if result:
                return result
            else:

                return []
        except Exception as e:
            # 捕获并打印异常
            logger.error('DealServerData:load_username_account_data', exc_info=True)
            return []

    def save_cj_data(self,data):
        try:
            sql = "insert into user_trader(id, username, date_time,cj_nr,cj_status,rq,gpdm,czlx) values (%s,%s,%s,%s,%s,%s,%s,%s)"


            username = data['username']
            id = self.getuuid()
            cj_nr = str(data['cj_nr'])
            gpdm = data['cj_nr']["stock_code"].split(".")[0]
            date_time = str(data['date_time'])
            czlx = str(data['czlx'])
            rq = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").date()
            cj_status = data['cj_status']
            params = (id, username, date_time,cj_nr,cj_status,rq,gpdm,czlx)
            conn = mysqlconnsingle()
            message = conn.insert_sql(sql, params)
            print(f"message:{message}")
            return message
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:save_cj_data发生异常', exc_info=True)

    def load_cj_data(self, data):
        try:
            # 从传入的数据中获取 username 和 rq
            username = data['username']
            rq = data['rq']
            czlx = data['czlx']
            # 构建 SQL 查询语句
            sql = "SELECT user_trader.id,user_trader.gpdm, user_trader.cj_nr,wcdata.gpmc FROM user_trader join wcdata on user_trader.gpdm=wcdata.gpdm WHERE user_trader.username = %s AND user_trader.rq = %s and user_trader.czlx=%s  order by user_trader.date_time asc"
            # 获取数据库连接
            conn = mysqlconnsingle()
            # 执行查询操作，传入查询参数
            result = conn.query_sql(sql, (username, rq,czlx))
            # 返回查询结果
            return result
        except Exception as e:
            # 捕获并打印异常
            logger.error('DealServerData:load_cj_data', exc_info=True)
            return []
    #加载卖出的成交数据
    def load_sell_data(self, data):
        try:
            # 从传入的数据中获取 username 和 rq
            username = data['username']
            rq = data['rq']
            # 构建 SQL 查询语句
            sql = "SELECT user_trader.id,user_trader.gpdm, user_trader.cj_nr,wcdata.gpmc FROM user_trader join wcdata on user_trader.gpdm=wcdata.gpdm WHERE user_trader.username = %s AND user_trader.rq = %s and user_trader.czlx='sell'  order by user_trader.date_time asc"
            # 获取数据库连接
            conn = mysqlconnsingle()
            # 执行查询操作，传入查询参数
            result = conn.query_sql(sql, (username, rq))
            # 返回查询结果
            return result
        except Exception as e:
            # 捕获并打印异常
            logger.error('DealServerData:load_sell_data', exc_info=True)
            return []

    def get_gpmc_by_gpdm(self, data):
        try:
            params = data['params']
            # 确保 params 是列表类型
            if not isinstance(params, list):
                raise ValueError("params 参数必须是列表")
            # 构建 SQL 查询语句，使用占位符 %s 来避免 SQL 注入
            query = f"SELECT gpdm, gpmc,xj FROM wcdata WHERE gpdm IN ({','.join(['%s'] * len(params))})"
            # 获取数据库连接
            mysql = mysqlconnsingle()
            # 执行查询，确保传递的参数和占位符数量一致
            params = tuple(params)
            result = mysql.query_sql(query, params)
            return result
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:get_gpmc_by_gpdm', exc_info=True)

            return []

    def update_sell_position(self, data):
        try:
            # 从传入的数据中获取 username 和 mcsz
            username = data['username']
            mcsz = data['mcsz']

            # 查询 username 是否存在
            select_sql = "SELECT id FROM username_mcsz WHERE username = %s"
            conn = mysqlconnsingle()
            result = conn.query_sql(select_sql, (username,))

            if result:
                # 如果 username 存在，更新 mcsz 字段
                update_sql = "UPDATE username_mcsz SET mcsz = %s WHERE username = %s"
                message = conn.insert_sql(update_sql, (mcsz, username))

            else:
                # 如果 username 不存在，插入新数据
                insert_sql = "INSERT INTO username_mcsz(id, username, mcsz) VALUES (%s, %s, %s)"
                id = self.getuuid()  # 生成唯一 ID
                message = conn.insert_sql(insert_sql, (id, username, mcsz))


        except Exception as e:
            # 捕获并打印异常
            logger.error('DealServerData:update_sell_position', exc_info=True)


    def get_mcsz_by_username(self, data):
        try:
            # 从传入的数据中获取 username
            username = data['username']
            # 构建 SQL 查询语句
            select_sql = "SELECT mcsz FROM username_mcsz WHERE username = %s"
            conn = mysqlconnsingle()
            result = conn.query_sql(select_sql, (username,))
            # 如果查询结果不为空，返回 mcsz

            return result

        except Exception as e:
            # 捕获并打印异常
            logger.error('DealServerData:get_mcsz_by_username', exc_info=True)
            return {"mcsz": None, "status": "failed", "message": str(e)}

    def get_gp_close_datas(self, data):
        try:
            params=data['codes_list']
            str = f"SELECT gpmc,gpdm,xj,ltsz,ltgbnum,close_pre_day_price,vol FROM wcdata WHERE gpdm IN ({','.join(['%s'] * len(params))})"
            mysql = mysqlconnsingle()
            result = mysql.query_sql(str, params)
            return result
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:get_gp_close_datas发生异常', exc_info=True)

    def get_rencent_datas(self, data):
        try:
            params=data['params']

            API = jsp.Init_jsp()
            js = jspSJ()
            now = datetime.now()
            rq = now.strftime("%Y-%m-%d")
            all=[]
            for item in params:

                da=json.loads(str(js.getrxsj( item, rq, jsp, API)))
                all.append(da)
            jsp.destroy_jsp(API)
            return all
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:get_tick_datas', exc_info=True)

    import uuid
    from datetime import datetime, timedelta

    # 假设之前的类定义和导入部分已经存在，以下是修改后的 yz_account 方法
    def yz_account(self, params):
        try:
            # 获取用户名
            acc = params.get('acc')
            if not acc:
                logger.error("yz_account: 缺少必要的'username'参数")
                return {"status": "error", "message": "缺少必要的'username'参数"}

            # 数据库操作
            conn = mysqlconnsingle()
            # 1. 检查用户是否存在
            select_sql = "SELECT id, username, start_rq, end_rq, zh_lx,acc,qq,wechat FROM username WHERE acc = %s"
            result = conn.query_sql(select_sql, (acc,))
            print(result)

            # 用户存在，返回查询结果
            if result:
                user_data = result[0]
                return user_data
            else:
                return None
        except Exception as e:
            logger.error('DealServerData:yz_account发生异常', exc_info=True)
            return {"status": "error", "message": str(e)}

    def save_register_zh(self, params):
        try:
            acc=params["acc"]
            qq = params["qq"]
            wechat = params["wechat"]
            today = datetime.now().date()
            dl_date = today.strftime('%Y-%m-%d')
            id = self.getuuid()
            # 数据库操作
            conn = mysqlconnsingle()
            insert_sql = """
                            INSERT INTO username 
                            (id, acc, dl_date,qq,wechat) 
                            VALUES (%s, %s, %s, %s, %s)
                        """
            # 执行插入
            params = (id, acc, dl_date,qq,wechat)
            result=conn.insert_sql(insert_sql, params)
            return result
        except Exception as e:
            logger.error('DealServerData:save_register_zh发生异常', exc_info=True)
            return {"status": "error", "message": str(e)}

    def check_duplicate_zh(self, data):
        try:
            # 从 data 中提取参数
            qq = data.get('qq')
            wechat = data.get('wechat')
            acc = data.get('acc')


            # 参数校验
            if not str:
                logger.error('check_duplicate_zh: 缺少 qq 或 wechat 参数')
                return {"message": "参数缺失"}

            # 构建 SQL 查询
            sql = "SELECT qq,wechat FROM username WHERE (qq = %s OR wechat = %s OR acc=%s)"
            params = (qq, wechat,acc)

            # 执行查询
            conn = mysqlconnsingle()
            result = conn.query_sql(sql, params)
            return result
        except Exception as e:
            logger.error('DealServerData:check_duplicate_zh发生异常', exc_info=True)
            return {"message": "error"}

    def query_username_power(self, data):
        try:
            # 从传入的数据中提取参数
            wechat = data.get('wechat')
            qq = data.get('qq')
            acc = data.get('acc')

            # 构建动态查询条件和参数列表
            conditions = []
            params = []
            if wechat:
                conditions.append("wechat = %s")
                params.append(wechat)
            if qq:
                conditions.append("qq = %s")
                params.append(qq)
            if acc:
                conditions.append("acc = %s")
                params.append(acc)

            # 如果没有提供任何查询条件，返回错误信息
            if not conditions:
                return {"status": "error", "message": "必须提供至少一个查询条件（wechat、qq 或 acc）"}

            # 构建完整的 SQL 查询语句
            sql = "SELECT id, username, start_rq, end_rq, zh_lx, acc, qq, wechat,dl_date FROM username WHERE "
            sql += " OR ".join(conditions)  # 使用 OR 连接多个条件

            # 执行数据库查询
            conn = mysqlconnsingle()
            result = conn.query_sql(sql, params)

            # 返回查询结果（可能包含多个匹配项）
            return result

        except Exception as e:
            logger.error('DealServerData:query_username_power 发生异常', exc_info=True)
            return {"status": "error", "message": str(e)}

    def add_wechat(self, data):
        try:
            # 从传入的数据中提取参数
            id = data.get('id')
            wechat = data.get('wechat')
            print(wechat)
            # 参数校验
            if not id or not wechat:
                logger.error('add_wechat: 缺少必要的 id 或 wechat 参数')
                return {"status": "error", "message": "缺少必要的 id 或 wechat 参数"}

            # 首先查询该 id 是否存在
            select_sql = "SELECT id FROM username WHERE id = %s"
            conn = mysqlconnsingle()
            result = conn.query_sql(select_sql, (id,))

            if not result:
                logger.error(f'add_wechat: 未找到 id 为 {id} 的记录')
                return {"status": "error", "message": f"未找到 id 为 {id} 的记录"}

            # 如果记录存在，更新 wechat 字段
            update_sql = "UPDATE username SET wechat = %s WHERE id = %s"
            message = conn.insert_sql(update_sql, (wechat, id))

            return message

        except Exception as e:
            logger.error('DealServerData:add_wechat 发生异常', exc_info=True)
            return {"status": "error", "message": str(e)}
    def add_qq(self, data):
        try:
            # 从传入的数据中提取参数
            id = data.get('id')
            qq = data.get('qq')

            # 参数校验
            if not id or not qq:
                logger.error('add_wechat: 缺少必要的 id 或 wechat 参数')
                return {"status": "error", "message": "缺少必要的 id 或 wechat 参数"}

            # 首先查询该 id 是否存在
            select_sql = "SELECT id FROM username WHERE id = %s"
            conn = mysqlconnsingle()
            result = conn.query_sql(select_sql, (id,))

            if not result:
                logger.error(f'add_wechat: 未找到 id 为 {id} 的记录')
                return {"status": "error", "message": f"未找到 id 为 {id} 的记录"}

            # 如果记录存在，更新 wechat 字段
            update_sql = "UPDATE username SET qq = %s WHERE id = %s"
            message = conn.insert_sql(update_sql, (qq, id))

            return message

        except Exception as e:
            logger.error('DealServerData:add_qq 发生异常', exc_info=True)
            return {"status": "error", "message": str(e)}

    def add_acc(self, data):
        try:
            # 从传入的数据中提取参数
            id = data.get('id')
            acc = data.get('acc')

            # 参数校验
            if not id or not acc:
                logger.error('add_wechat: 缺少必要的 id 或 wechat 参数')
                return {"status": "error", "message": "缺少必要的 id 或 wechat 参数"}

            # 首先查询该 id 是否存在
            select_sql = "SELECT id FROM username WHERE id = %s"
            conn = mysqlconnsingle()
            result = conn.query_sql(select_sql, (id,))

            if not result:
                logger.error(f'add_wechat: 未找到 id 为 {id} 的记录')
                return {"status": "error", "message": f"未找到 id 为 {id} 的记录"}

            # 如果记录存在，更新 wechat 字段
            update_sql = "UPDATE username SET acc = %s WHERE id = %s"
            message = conn.insert_sql(update_sql, (acc, id))

            return message

        except Exception as e:
            logger.error('DealServerData:add_acc 发生异常', exc_info=True)
            return {"status": "error", "message": str(e)}
    def add_zh_lx(self, data):
        try:
            # 从传入的数据中提取参数
            id = data.get('id')
            zh_lx = data.get('zh_lx')

            # 参数校验
            if not id or not zh_lx:
                logger.error('add_wechat: 缺少必要的 id 或 wechat 参数')
                return {"status": "error", "message": "缺少必要的 id 或 wechat 参数"}

            # 首先查询该 id 是否存在
            select_sql = "SELECT id FROM username WHERE id = %s"
            conn = mysqlconnsingle()
            result = conn.query_sql(select_sql, (id,))

            if not result:
                logger.error(f'add_wechat: 未找到 id 为 {id} 的记录')
                return {"status": "error", "message": f"未找到 id 为 {id} 的记录"}

            # 如果记录存在，更新 wechat 字段
            update_sql = "UPDATE username SET zh_lx = %s WHERE id = %s"
            message = conn.insert_sql(update_sql, (zh_lx, id))

            return message

        except Exception as e:
            logger.error('DealServerData:add_zh_lx 发生异常', exc_info=True)
            return {"status": "error", "message": str(e)}

    def add_rq(self, data):
        try:
            # 从传入的数据中提取参数
            id = data.get('id')
            start_rq = data.get('start_rq')
            end_rq = data.get('end_rq')

            # 参数校验
            if not id or not start_rq or not end_rq:
                logger.error('add_rq: 缺少必要的 id 或 add_rq 参数')
                return {"status": "error", "message": "缺少必要的 id 或 add_rq 参数"}

            # 首先查询该 id 是否存在
            select_sql = "SELECT id FROM username WHERE id = %s"
            conn = mysqlconnsingle()
            result = conn.query_sql(select_sql, (id,))

            if not result:
                logger.error(f'add_rq: 未找到 id 为 {id} 的记录')
                return {"status": "error", "message": f"未找到 id 为 {id} 的记录"}

            # 如果记录存在，更新 wechat 字段
            update_sql = "UPDATE username SET start_rq = %s,end_rq= %s  WHERE id = %s"
            message = conn.insert_sql(update_sql, (start_rq,end_rq,id))

            return message

        except Exception as e:
            logger.error('DealServerData:add_rq 发生异常', exc_info=True)
            return {"status": "error", "message": str(e)}

    def getrxsj_by_one_min(self,data):
        try:
            today = datetime.today()
            rq = today.strftime('%Y-%m-%d')
            zh_lx = data['zh_lx']
            code = data['gpdm']

            API = jsp.Init_jsp()
            js = jspSJ()
            da = js.getrxsj_by_one_min( code, rq, jsp, API)

            jsp.destroy_jsp(API)
            return da
        except Exception as e:  # 捕获所有其他异常
            logger.error('DealServerData:get_tick_datas', exc_info=True)


