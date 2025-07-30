import uuid
from Server.ConMysql import mysqlconnsingle
import json

def getuuid():
    uuid_32 = uuid.uuid4().hex
    return uuid_32
class Holiday():
    def __init__(self):
        super(Holiday, self).__init__()
    # 中国股市法定节假日列表（根据国务院假期安排，2025 年为例）
    def addholiday(self):
        holiday = [
            "2025-01-01",
            "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31", "2025-02-01", "2025-02-02", "2025-02-03", "2025-02-04",
            "2025-04-04", "2025-04-05", "2025-04-06",
            "2025-05-01", "2025-05-02", "2025-05-03", "2025-05-04", "2025-05-05",
            "2025-10-01", "2025-10-02", "2025-10-03", "2025-10-06", "2025-10-07", "2025-10-08"
        ]
        st=str(holiday)
        sql = """
                        insert into holiday(id,holiday,year)
                        values(%s,%s,%s)
                     """
        id =getuuid()
        year='2025'
        conn = mysqlconnsingle()
        conn.insert_sql(sql, (id,st,year))







