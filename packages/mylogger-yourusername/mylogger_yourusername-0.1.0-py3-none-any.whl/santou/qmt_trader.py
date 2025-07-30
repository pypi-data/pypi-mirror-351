import threading
from xtquant import xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import sys
import random
from datetime import datetime
from santou.DeaiClientData import DeaiClientData
from santou.logging.log import logger

class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print("connection lost")

    def on_stock_order(self, order):
        print("on order callback:")
        print(order.stock_code, order.order_status, order.order_sysid)

    def on_stock_asset(self, asset):
        print("on asset callback")
        print(asset.account_id, asset.cash, asset.total_asset)

    def on_stock_trade(self, trade):
        print("on trade callback")
        print(trade.account_id, trade.stock_code, trade.order_id)

    def on_stock_position(self, position):
        print("on position callback")
        print(position.stock_code, position.volume)

    def on_order_error(self, order_error):
        print("on order_error callback")
        print(order_error.order_id, order_error.error_id, order_error.error_msg)

    def on_cancel_error(self, cancel_error):
        print("on cancel_error callback")
        print(cancel_error.order_id, cancel_error.error_id, cancel_error.error_msg)

    def on_order_stock_async_response(self, response):
        print("on_order_stock_async_response")
        print(response.account_id, response.order_id, response.seq)

    def on_account_status(self, status):
        print("on_account_status")
        print(status.account_id, status.account_type, status.status)


class qmt_trader:
    def __init__(self, path, account, username):
        self.path = path
        self.account = account
        self.acc = StockAccount(account)
        self.session_id = random.randint(1, 1000000) + datetime.now().second
        self.xt_trader = None
        self.init_xt_trader()
        self.username = username
       # self.get_cancellable_stocks()

    def get_qmttrader(self):
        if self.xt_trader:
            return self.xt_trader

    def get_account(self):
        if self.account:
            return self.account
        else:
            return None

    def init_xt_trader(self):
        if self.xt_trader is None:
            self.message = {}
            try:
                xt_trader = XtQuantTrader(self.path, self.session_id)
                callback = MyXtQuantTraderCallback()
                xt_trader.register_callback(callback)
                xt_trader.start()
                connect_result = xt_trader.connect()

                if connect_result != 0:
                    self.message["result"] = "fail"
                    self.message["message"] = "连接失败，请登录券商QMT软件！"
                    xt_trader=None
                    return self.message

                subscribe_result = xt_trader.subscribe(self.acc)
                if subscribe_result != 0:
                    self.message["result"] = "fail"
                    self.message["message"] = "连接失败，请检查账号是否有误或者是否有交易权限！"
                    xt_trader = None
                    return self.message
                #成功了返回
                self.xt_trader=xt_trader
                self.message["result"] = "ok"
                self.message["message"] = "连接成功！"
                return self.message

            except Exception as e:
                self.message["result"] = "fail"
                self.message["message"] = f"连接失败，错误: {str(e)}"
                xt_trader = None
                logger.error('qmt_trader:init_xt_trader:连接失败', exc_info=True)
                return self.message



    def queryye(self):
        if self.xt_trader is None:
            self.init_xt_trader()

        asset = self.xt_trader.query_stock_asset(self.acc)
        return float(asset.cash) if asset else 0

    def xiadan(self, stock_code, num, price, ye, zxzt_total, db_ym1,buy_lx):
        params = {}
        czlx = buy_lx
        try:
            num_int = int(num)
            price_float = float(price)

            fix_result_order_id = self.xt_trader.order_stock(
                self.acc,
                stock_code,
                xtconstant.STOCK_BUY,
                num_int,
                xtconstant.FIX_PRICE,
                price_float,
                'strategy_name',
                'remark'
            )

            if fix_result_order_id is None or fix_result_order_id < 0:
                cj_status = "0"
                params["cj_zt"] = "买入失败"
                self._async_cj_data(params, cj_status, zxzt_total, stock_code, db_ym1, czlx)
                return
            #print(f"fix_result_order_id:{fix_result_order_id}")
            order_status = self.query_order_status(fix_result_order_id)
            cj = price_float * num_int
            zb = cj / float(ye)
            params["stock_code"] = stock_code
            params["zb"] = zb
            params["num"] = num
            params["price"] = price
            #print(f"fix_result_order_id: {fix_result_order_id}")
            #print(f"order_status:{order_status}")
            # 成交信息
            params["cj_zt"] = "已下单"
            #print(f"cj_zt:{self.query_order_status_message(order_status)}")
            cj_status = "1"
            self._async_cj_data(params, cj_status, zxzt_total, stock_code, db_ym1, czlx)
            return
        except Exception as e:
            params["cj_zt"] = "买入失败"
            cj_status = "0"
            self._async_cj_data(params, cj_status, zxzt_total, stock_code, db_ym1, czlx)
            logger.error('qmt_trader:xiadan:买入错误错误', exc_info=True)
            return

    #异步操作避免线程堵塞
    def _async_cj_data(self, params, cj_status, zxzt_total, stock_code, db_ym1, czlx):
        thread = threading.Thread(target=self.cj_data, args=(params, cj_status, zxzt_total, stock_code, db_ym1, czlx))
        thread.start()

    # 保存交易记录，便于查看
    def cj_data(self, params, cj_status, zxzt_total, stock_code, db_ym1, czlx):
        if cj_status == "1":

            #下单成功才能设置
            db_ym1.update_zxzt_total.emit(zxzt_total)
            #db_ym1.dbsm2.setText(zxzt_total)
            #db_ym1.win._model

        action = 'save_cj_data'
        deal = DeaiClientData()
        re = deal.save_cj_data(action, params, self.username, cj_status, czlx)
        if re["message"] == "success":
            #通知更新提示框
            db_ym1.tsk.emit()

    def ch_connection_status(self):
        return self.message

    def sell_stock(self, stock_code, num, price,sell):
        params={}
        params["stock_code"] = stock_code
        params["zb"] = "0"
        params["num"] = num
        params["price"] = price

        try:
            positions = self.xt_trader.query_stock_positions(self.acc)
            if not positions:
                return {"status": "error", "message": "没有持仓"}

            available_volume = next(
                (p.volume for p in positions if p.stock_code == stock_code),
                0
            )
            if available_volume <= 0:
                return {"status": "error", "message": "无可用持仓"}

            num_int = min(int(num), available_volume)
            price_float = float(price)

            fix_result_order_id = self.xt_trader.order_stock(
                self.acc,
                stock_code,
                xtconstant.STOCK_SELL,
                num_int,
                xtconstant.FIX_PRICE,
                price_float,
                'strategy_name',
                'remark'
            )
            if fix_result_order_id is None or fix_result_order_id < 0:
                params["cj_zt"] = "卖出失败！"
                cj_status = "0"
                self._async_sell_data(params, cj_status, stock_code, sell)
                return {"status": "error", "message": "卖出失败"}
            #刷新界面列表
            sell.on_combo_box_changed()

            #卖出成功
            params["cj_zt"] = "已下单"
            cj_status = "1"
            self._async_sell_data(params, cj_status, stock_code, sell)

            return {"status": "success", "message": "卖出成功！"}
        except Exception as e:
            params["cj_zt"] = "卖出失败！"
            cj_status = "0"
            self._async_sell_data(params, cj_status, stock_code, sell)
            logger.error('qmt_trader:sell_stock:卖出错误错误', exc_info=True)
            return {"status": "error", "message": f"卖出异常: {str(e)}"}

        # 异步操作避免线程堵塞
        #卖出失败的操作


    def _async_sell_data(self, params, cj_status,  stock_code, sell):
        sellthread = threading.Thread(target=self.sell_data, args=(params, cj_status, stock_code, sell))
        sellthread.start()

        # 保存交易记录，更新列表
    def sell_data(self, params, cj_status, stock_code, sell):
        czlx = "sell"
        action = 'save_cj_data'
        deal = DeaiClientData()
        re = deal.save_cj_data(action, params, self.username, cj_status, czlx)

        #保存成功后刷新数据
        if re["message"] == "success":
            sell.data_updated_signal.emit(stock_code)  # 发射信号而不是直接调用方法

    def cancel_unfilled_orders(self):
        orders = self.xt_trader.query_stock_orders(self.acc)
        if not orders:
            return

        for order in orders:
            if order.order_status == xtconstant.ORDER_REPORTED:
                self.xt_trader.cancel_order_stock(self.acc, order.order_id)

    def cancel_order(self, order_id):
        if self.xt_trader is None:
            self.init_xt_trader()

        cancel_result = self.xt_trader.cancel_order_stock(self.acc, order_id)
        return cancel_result == 0

    def query_order_status(self, order_id):
        orders = self.xt_trader.query_stock_orders(self.acc)

        for order in orders:
            if order.order_id == order_id:
                print(f"order_status:{order.order_status}")
                print(f"self:{self.query_order_status_message(order.order_status)}")
                return order.order_status
        return None

    def query_order_status_message(self, order_id):
        order_status_map = {
            "48": "未报",
            "49": "待报",
            "50": "已报未成交",
            "51": "已报待撤",
            "52": "部分成交，剩下的待撤",
            "53": "部分成交，剩下的已经撤单",
            "54": "已撤单",
            "55": "部分成交，剩下的待成交",
            "56": "已成交",
            "57": "废单",
            "255": "未知"
        }
        return order_status_map[f"{order_id}"]

    #def query_all_filled_stocks(self):

       # positions = self.xt_trader.query_stock_positions(self.acc)
        # 筛选出成交量大于 0 的持仓
        #filled_positions = [position for position in positions if position.volume > 0]
        #if len(positions) != 0:
          #  for position in positions:
             #   print("{0} {1} {2}".format(position.account_id, position.stock_code, position.volume))
           # return positions
    #查询所有的委托
    def check_weituo(self):
        # 查询当日所有的委托
        orders = self.xt_trader.query_stock_orders(self.acc)
        print("orders:", len(orders))
        if len(orders) != 0:
            print("last order:")
            print("{0} {1} {2}".format(orders[-1].stock_code, orders[-1].order_volume, orders[-1].price))

    #查询可撤销订单#
    def query_cancellable_orders(self):

        # 查询所有订单
        orders = self.xt_trader.query_stock_orders(self.acc)
        # 可撤单的状态列表
        cancellable_status = [
            xtconstant.ORDER_REPORTED,  # 已报未成交
            #xtconstant.ORDER_PENDING_CANCEL,  # 已报待撤
            #xtconstant.ORDER_PARTIAL_FILLED_PENDING_CANCEL,  # 部分成交，剩下的待撤
            #xtconstant.ORDER_PARTIAL_FILLED_PENDING_FILL,  # 部分成交，剩下的待成交
        ]
        # 筛选出可撤单的订单
        cancellable_orders = [order for order in orders if order.order_status in cancellable_status]
        if cancellable_orders:
            for order in cancellable_orders:
                print(
                    f"可撤单订单 - 股票代码: {order.stock_code},{order.order_volume}, 订单状态: {self.query_order_status_message(str(order.order_status))}, 订单ID: {order.order_id}")
            return cancellable_orders
        else:
            print("没有可撤单的订单")
            return []


    #查询可以卖出的持仓
    def query_all_filled_stocks(self):
        # 查询持仓
        positions = self.xt_trader.query_stock_positions(self.acc)
        sellable_stocks = []
        if positions:
            for position in positions:
                # 判断可用数量是否大于0
                if position.volume > 0 and position.can_use_volume > 0:
                    sellable_stocks.append({
                        'stock_code': position.stock_code,
                        'volume': position.volume,
                        'can_use_volume': position.can_use_volume, #可用数量
                        'market_value': position.market_value,  #市值
                        'avg_price': position.avg_price    #成本价
                    })
        return sellable_stocks
    #查询可撤销的持仓
    def query_today_cancellable_holdings(self):
        # 查询所有订单
        orders = self.xt_trader.query_stock_orders(self.acc)
        # 可撤单的状态列表
        cancellable_status = [
            xtconstant.ORDER_REPORTED,  # 已报未成交
            # 可以根据实际情况添加其他可撤单的状态
        ]
        # 筛选出可撤单的订单
        cancellable_orders = [order for order in orders if order.order_status in cancellable_status]

        cancellable_holdings = []
        if cancellable_orders:
            for order in cancellable_orders:
                # 对于可撤单的订单，记录其股票代码和订单数量
                cancellable_holdings.append({
                    'stock_code': order.stock_code,
                    'volume': order.order_volume
                })
                print(
                    f"可撤销持仓 - 股票代码: {order.stock_code}, 数量: {order.order_volume}, 订单状态: {self.query_order_status_message(str(order.order_status))}, 订单ID: {order.order_id}")

        else:
            print("没有可撤销的持仓")

        return cancellable_holdings

    #获取持仓
    def get_stock_positions(self):
        """
        获取股票持仓信息
        Returns:
            list: 返回持仓信息列表，每个元素为字典格式：
                {
                    'stock_code': 股票代码,
                    'volume': 持仓数量,
                    'available': 可用数量,
                    'cost_price': 成本价,
                    'market_value': 持仓市值
                }
        """
        try:
            # 查询持仓
            positions = self.xt_trader.query_stock_positions(self.acc)

            if not positions:
                print("当前没有持仓")
                return []

            position_list = []
            for position in positions:
                # 过滤无效持仓（持仓量<=0的）
                if position.volume <= 0:
                    continue

                position_data = {
                    'stock_code': position.stock_code,
                    'volume': position.volume,
                    'available': position.can_use_volume,
                    'cost_price': position.avg_price,  # 使用成本价字段
                    'market_value': position.market_value
                }
                position_list.append(position_data)

            return position_list

        except Exception as e:
            logger.error('qmt_trader:get_stock_positions:查询持仓失败', exc_info=True)
            return []

    #可撤单股票
    def get_cancellable_stocks(self):
        """
        找出所有可以被撤单的股票及其可撤数量总和
        Returns:
            list: 包含字典的列表，每个字典有'stock_code'和'cancellable_qty'键
                  例如：[{'stock_code': '600519.SH', 'cancellable_qty': 100}, ...]
        """
        cancellable_orders = self.query_cancellable_orders()
        stock_dict = {}

        for order in cancellable_orders:
            stock_code = order.stock_code
            # 计算该订单的可撤数量（委托量 - 已成交量）
            cancellable_qty = order.order_volume - order.traded_volume

            if cancellable_qty <= 0:
                continue  # 忽略无实际可撤数量的订单

            if stock_code in stock_dict:
                stock_dict[stock_code] += cancellable_qty
            else:
                stock_dict[stock_code] = cancellable_qty

        # 转换为目标格式
        result = [{'stock_code': code, 'cancellable_qty': qty} for code, qty in stock_dict.items()]

        return result

    def cancel_orders_by_stock_and_qty(self, stock_code, qty):
        """
        根据股票代码和数量撤单
        :param stock_code: 股票代码（如：'600519.SH'）
        :param qty: 要撤销的数量
        :return: 包含撤单结果的字典（success, cancelled_qty, message）
        """
        try:
            # 获取可撤订单列表
            cancellable_orders = self.query_cancellable_orders()
            # 过滤指定股票的订单并按时间排序（假设订单按时间升序排列，先撤最早的）
            target_orders = [order for order in cancellable_orders if order.stock_code == stock_code]

            if not target_orders:
                return {"success": False, "cancelled_qty": 0, "message": f"{stock_code}无相关可撤订单"}

            total_cancelled = 0
            success_orders = []

            # 遍历订单进行撤单
            for order in target_orders:
                if total_cancelled >= qty:
                    break

                # 计算该订单可撤数量
                cancellable_qty = order.order_volume - order.traded_volume
                if cancellable_qty <= 0:
                    continue

                # 执行撤单操作
                if self.cancel_order(order.order_id):
                    total_cancelled += cancellable_qty
                    success_orders.append(order.order_id)
                    logger.info(f"撤单成功 订单ID:{order.order_id} 数量:{cancellable_qty}")
                else:
                    logger.warning(f"撤单失败 订单ID:{order.order_id}")

            # 处理结果
            if total_cancelled > 0:
                if total_cancelled >= qty:
                    msg = f"成功撤单{total_cancelled}股（目标{qty}股）"
                    return {"success": True, "cancelled_qty": total_cancelled, "message": msg}
                else:
                    msg = f"部分撤单成功 实际撤单{total_cancelled}股（目标{qty}股）"
                    return {"success": False, "cancelled_qty": total_cancelled, "message": msg}
            else:
                return {"success": False, "cancelled_qty": 0, "message": "撤单失败"}

        except Exception as e:
            logger.error('cancel_orders_by_stock_and_qty 撤单异常', exc_info=True)
            return {"success": False, "cancelled_qty": 0, "message": f"撤单异常：{str(e)}"}