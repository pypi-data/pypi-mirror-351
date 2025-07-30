import pandas as pd
from Server.ConMysql import mysqlconnsingle
import pymysql

# 读取 CSV 文件
file_path = './个股简介.csv'  # 替换为你的 CSV 文件路径
df = pd.read_csv(file_path)

# 将 NaN 替换为空字符串（避免 MySQL 插入失败）
df = df.fillna('')

# 获取标题（列名）
columns = df.columns.tolist()
print("标题（列名）：")
print(columns)

# SQL 插入语句
sql = """
    INSERT INTO wcdata(id,gpdm,gpmc,zgbnum,ltgbnum,zyltnum,zycp,hy,gn)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

# 获取数据库连接
co = mysqlconnsingle()
conn = mysqlconnsingle().conn()

try:
    for index, row in df.iterrows():
        if index == 0:  # 跳过标题行
            continue

        # 提取每列数据，处理缺失值
        gpdm = row.iloc[0].split(".")[0] if pd.notna(row.iloc[0]) else ''
        id = row.iloc[0] if pd.notna(row.iloc[0]) else ''
        gpmc = row.iloc[1] if pd.notna(row.iloc[1]) else ''
        zgbnum = row.iloc[2] if pd.notna(row.iloc[2]) else ''
        ltgbnum = row.iloc[3] if pd.notna(row.iloc[3]) else ''
        zyltnum = row.iloc[4] if pd.notna(row.iloc[4]) else ''
        zycp = row.iloc[7] if pd.notna(row.iloc[7]) else ''
        hy = row.iloc[8] if pd.notna(row.iloc[8]) else ''
        gn = row.iloc[9] if pd.notna(row.iloc[9]) else ''

        # 插入数据
        co.in_sql(sql, (id, gpdm, gpmc, zgbnum, ltgbnum, zyltnum, zycp, hy, gn), conn)

    # 提交事务
    conn.commit()

except pymysql.MySQLError as e:
    print(f"插入操作失败，错误信息: {e}")
    conn.rollback()  # 回滚事务

finally:
    if conn and conn.open:
        conn.close()
