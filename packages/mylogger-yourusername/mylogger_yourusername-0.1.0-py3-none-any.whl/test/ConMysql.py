import pymysql
import json
from Server.logging.log import logger
# 创建一个 MySQL 连接单例用法
class mysqlconnsingle:
    conn1 = None

    def conn(self):
        global conn1
        if self.conn1 is None:
            try:
                self.conn1 = pymysql.connect(
                    host='localhost',
                    user='root',
                    passwd='',
                    database='data_gp',
                    charset='utf8',
                    port=3306
                )
                print("数据库连接成功！")
            except pymysql.MySQLError as e:
                logger.error('ConMysql:conn:数据库连接失败，错误信息', exc_info=True)
                raise e
        return self.conn1


    def insert_sql(self,sql, params):

        message={}
        conn = mysqlconnsingle().conn()
        try:
            cu = conn.cursor()
            cu.execute(sql, params)
            conn.commit()
            message["message"]="success"
            print("插入操作成功！")
            return message
        except pymysql.MySQLError as e:
            logger.error('ConMysql:conn:插入操作失败，错误信息', exc_info=True)
            conn.rollback()  # 回滚事务
            message["message"] = "fail"
            return message
        finally:
            if conn:
                conn.close()

    def in_sql(self,sql, params,conn):
        cu = conn.cursor()
        cu.execute(sql, params)

    def query_sql(self,sql,params):
        conn = mysqlconnsingle().conn()
        try:
            cu = conn.cursor(pymysql.cursors.DictCursor)  # 使用 DictCursor 返回字典形式的查询结果
            cu.execute(sql,params)
            data = cu.fetchall()  # 返回一个字典形式的结果列表

            if data:
                #print("JSON 格式查询结果：", data)
                return data
            else:
                print("未取到值")
                #return json.dumps({"message": "No data found"}, ensure_ascii=False)

        except pymysql.MySQLError as e:
            logger.error('ConMysql:query_sql:查询操作失败，错误信息', exc_info=True)
            #return json.dumps({"message": f"Query failed: {e}"}, ensure_ascii=False)
        finally:
            if conn:
                conn.close()

    def del_update_sql(self,sql):
        try:
            conn = mysqlconnsingle().conn()
            cu = conn.cursor()
            cu.execute(sql)
            conn.commit()
            print("删除/更新操作成功！")
        except pymysql.MySQLError as e:
            logger.error('ConMysql:del_update_sql:删除/更新操作失败，错误信息', exc_info=True)
            conn.rollback()  # 回滚事务
        finally:
            if conn:
                conn.close()

    def query_one_sql(self,sql):
        conn = mysqlconnsingle().conn()
        try:
            cu = conn.cursor(pymysql.cursors.DictCursor)  # 使用 DictCursor 返回字典形式的查询结果
            cu.execute(sql)
            data = cu.fetchone()  # 返回一个字典形式的结果列表

            if data:
                #print("JSON 格式查询结果：", data)
                return data
            else:
                print("未取到值")
                # return json.dumps({"message": "No data found"}, ensure_ascii=False)

        except pymysql.MySQLError as e:
            print(f"查询操作失败，错误信息: {e}")
            logger.error('ConMysql:query_one_sql:查询操作失败，错误信息', exc_info=True)
            # return json.dumps({"message": f"Query failed: {e}"}, ensure_ascii=False)
        finally:
            if conn:
                conn.close()
        # 更新数据函数
    def update_wcdata(self,conn,sql,update_data):
        message = {}
        conn = mysqlconnsingle().conn()
        try:
            cu = conn.cursor()
            cu.execute(sql, list(update_data.values()))
            conn.commit()
            message["message"] = "success"
            print("插入操作成功！")
            return message
        except pymysql.MySQLError as e:
            logger.error('ConMysql:conn:插入操作失败，错误信息', exc_info=True)
            conn.rollback()  # 回滚事务
            message["message"] = "fail"
            return message
        finally:
            if conn:
                conn.close()

    def query_data_no_conn(self,cu,sql,params):
        try:
            cu.execute(sql, params)
            data = cu.fetchall()  # 返回一个字典形式的结果列表
            if data:
                # print("JSON 格式查询结果：", data)
                return data
            else:
                print("未取到值")
        except pymysql.MySQLError as e:
            logger.error('ConMysql:query_data_no_conn:查询操作失败，错误信息', exc_info=True)


