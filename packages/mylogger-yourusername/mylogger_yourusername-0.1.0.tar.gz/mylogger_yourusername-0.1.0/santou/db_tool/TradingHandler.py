import threading
from santou.logging.log import logger

class TradingHandler:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TradingHandler, cls).__new__(cls)
            return cls._instance
    #将下单查询上锁，实现单例访问，其他程序也能调用这个功能
    def handle_trading(self, db1, code, price,worker,buy_lx):

        try:
            fee_ratio = 0.005  # 佣金+印花税等
            with db1.strategy_lock:
                ye = float(db1.qmt.queryye())
                available_funds = ye
                if db1.zzje == 0:
                    db1.zzje = ye
                    available_funds = min(db1.zzje, ye)
                else:
                    available_funds = min(db1.zzje, ye)

                # 判断每个股票输入是空的情况下
                mzgpmre = available_funds
                if len(db1.jon["mzgpmrje"]) == 0 or db1.jon["mzgpmrje"]=="0":
                    mzgpmre = available_funds
                else:
                    mzgpmre = float(db1.jon["mzgpmrje"])

                if available_funds >= mzgpmre:
                    available_after_fee = mzgpmre * (1 - fee_ratio)
                    result = int(available_after_fee / price)
                    if result< 100:

                        params = {
                            "stock_code": code,
                            "zb": 0,
                            "num": 100,
                            "price": price,
                            "cj_zt": "资金不足，请检查资金余额、买入资金总金额以及每只股票买入金额设置是否正确！"
                        }
                        db1.db_ym1.jebz_info.emit(params)  # 发射 dict 到 tjd_db 的信号

                        return

                    num = (result // 100) * 100
                    db1.price_list.pop(code, None)
                    db1.decrease_zxzt_total()  # 替换原有的 zxzt_total 修改

                    db1.qmt.xiadan(db1.add_exchange_suffix(code), num, price, ye, db1.zxzt_total, db1.db_ym1,buy_lx)
                    db1.zzje -= mzgpmre
                else:
                    available_after_fee = available_funds * (1 - fee_ratio)
                    result = int(available_after_fee / price)
                    if  result< 100:

                        params = {
                            "stock_code": code,
                            "zb": 0,
                            "num": 100,
                            "price": price,
                            "cj_zt": "资金不足，请检查资金余额、买入资金总金额以及每只股票买入金额设置是否正确！"
                        }
                        db1.db_ym1.jebz_info.emit(params)  # 发射 dict 到 tjd_db 的信号
                        return
                    num = (result // 100) * 100
                    #从股票池中删除
                    db1.price_list.pop(code, None)
                    ye = float(db1.qmt.queryye())
                    db1.decrease_zxzt_total()  # 替换原有的 zxzt_total 修改
                    db1.qmt.xiadan(db1.add_exchange_suffix(code), num, price, ye, db1.zxzt_total, db1.db_ym1,buy_lx)
                    db1.zzje -= available_funds
        except Exception as e:
            logger.error('TradingHandler:handle_trading', exc_info=True)
            worker.finished.emit()
            return