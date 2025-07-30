from Server.ConMysql import mysqlconnsingle
import uuid
import json
import pymysql


from Server.ConMysql import mysqlconnsingle
import uuid
import json
import pymysql


def getuuid():
    uuid_32 = uuid.uuid4().hex
    return uuid_32
#概念股票对应
def query_data():
    try:
        sql = "select gn,gpdm,gpmc from wcdata"
        # 使用 mysqlconnsingle 的静态方法 query_sql
        result = mysqlconnsingle.query_sql(sql, params=None)

        if not result:  # 如果结果为空
            print("查询结果为空")
            return

        # 获取数据库连接
        co = mysqlconnsingle().conn()

        for row in result:
            if row['gn']:
                gn = row['gn']
                gpdm = row['gpdm']
                gpmc = row['gpmc']
                gns = gn.split(";")

                for gn in gns:
                    if gn:
                        sql = "insert into gngp(id,gn,gpdm,gpmc) values (%s,%s,%s,%s)"
                        id = getuuid()
                        mysqlconnsingle.in_sql(sql, (id, gn, gpdm, gpmc), co)  # 使用 co 作为连接对象
                        #print(f"{gn},{gpmc}")
        co.commit()
    except pymysql.MySQLError as e:
        print(f"插入操作失败，错误信息: {e}")
        if co:
            co.rollback()  # 回滚事务
    finally:
        if co:
            co.close()


query_data()