from santou.gjqmt.db2_qmt_trader import qmt_trader as qmt_trader1
from santou.qmt_trader import qmt_trader as qmt_trader2
class queryzt1:
    def queryzt1(self):
        qmt=qmt_trader1(r'D:\国金证券QMT交易端\userdata_mini','8886508668')
        qmt.query_order_status(1107627931)

    def queryzt2(self):
        qmt = qmt_trader2(r'D:\国金证券QMT交易端\userdata_mini', '8886508668')
        qmt.query_order_status(1107627931)


zt=queryzt1()
zt.queryzt1()
print("123")
zt.queryzt2()
