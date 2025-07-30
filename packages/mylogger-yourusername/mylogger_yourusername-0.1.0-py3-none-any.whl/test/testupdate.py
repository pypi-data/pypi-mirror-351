import pymysql

def update_mysql_table(host, user, password, database, table_name, update_data, condition):
    # 构造动态 SQL 语句
    fields = ", ".join([f"{key} = %s" for key in update_data.keys()])
    sql = f"UPDATE {table_name} SET {fields} WHERE {condition}"

    # 数据库连接配置
    try:
        # 连接到 MySQL 数据库
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        with connection.cursor() as cursor:
            # 执行更新语句
            cursor.execute(sql, list(update_data.values()))
            connection.commit()
            print(f"更新成功: {cursor.rowcount} 行受影响")
    except pymysql.MySQLError as e:
        print(f"MySQL 错误: {e}")
    finally:
        if connection:
            connection.close()

# 示例调用
if __name__ == "__main__":
    host = "localhost"           # 数据库主机
    user = "root"                # 数据库用户名
    password = "password123"     # 数据库密码
    database = "test_db"         # 数据库名称
    table_name = "users"         # 表名称
    update_data = {"name": "Jane Doe", "age": 28}  # 要更新的字段和值
    condition = "id = 1"         # 更新条件

    update_mysql_table(host, user, password, database, table_name, update_data, condition)
