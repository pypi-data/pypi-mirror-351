from santou.DeaiClientData import DeaiClientData


class yztool():
    def yzbk(self,jon,gpdm):
        for item in jon['bk']:
            if item=="主板":
               if gpdm.startswith('00') or gpdm.startswith('60'):
                   return True
            if item=="创业板":
                if gpdm.startswith('30'):
                    return True
            if item=="科创板":
                if gpdm.startswith('688'):
                    return True
    def yzdb(self,jon,ztzt):
        for item in jon['db']:
            if item=='首板':
                if ztzt=="0":
                    return True
            if item == '二板':
                if ztzt == "1":
                    return True
            if item == '三板及以上':
                if int(ztzt) >=2:
                    return True

    def yzltsz(self,jon,ltsz):
        if "ltsz" in jon:
            ltsz=float(ltsz)
            if len(jon['ltsz'][0]) == 0 and len(jon['ltsz'][1]) == 0:
                return True
            if len(jon['ltsz'][0])>0 and len(jon['ltsz'][1])>0:
              if float(jon['ltsz'][0])<ltsz and float(jon['ltsz'][1])>ltsz:
                  return True
              else:
                  return False
            if len(jon['ltsz'][0])==0 and len(jon['ltsz'][1]) > 0:
                if len(jon['ltsz'][1])>ltsz:
                    return True
                else:
                    return False
            if len(jon['ltsz'][0])>0 and len(jon['ltsz'][1]) ==0:
                if len(jon['ltsz'][0])<ltsz:
                    return True
                else:
                    return False
        else:
            return True

    def yzprice(self,jon,price):
        if "price" in jon:
            price = float(price)
            if len(jon['price'][0])==0 and len(jon['price'][1])== 0:
                return True
            if len(jon['price'][0]) > 0 and len(jon['price'][1]) > 0:
                if float(jon['price'][0]) < price and float(jon['price'][1]) > price:
                    return True
                else:
                    return False
            if len(jon['price'][0]) == 0 and len(jon['price'][1]) > 0:
                if len(jon['price'][1]) > price:
                    return True
                else:
                    return False
            if len(jon['price'][0]) > 0 and len(jon['price'][1]) == 0:
                if len(jon['price'][0]) < price:
                    return True
                else:
                    return False
        else:
            return True

    def yzfbzj(self,jon,gpdm,price):
        #存在封板资金,需要查询验证
        if "fbzj" in jon:
            if len(jon["fbzj"])>0:
                tick_fbzj=self.getfbzj(gpdm,price)
                if tick_fbzj>float(jon['fbzj']):
                    return True
                else:
                    return False
            else:
                return True
        else:
             return True
    #涨停且无封单买入
    def zt_wfdmr(self,jon,gpdm,price):
        if "涨停且卖一无封单时买入" in jon:
            return True
        else:
            return True
    #触发涨停价时买入
    def cfztj(self, jon,gpdm,price):
        if "触发涨停价时买入" in jon:
            return self.get_zt_my_no(gpdm,price)
        else:
            return True

    # 只剩卖一1档时买入,要带上昨天收盘价
    def myyd_mr(self, jon,gpdm):
        if "只剩卖一一档时买入" in jon:
            return True
        else:
            return True

    # 只剩卖一卖二两档时买入
    def mymeld_mr(self, jon,gpdm):
        if "只剩卖一卖二两档时买入" in jon:
            return True
        else:
            return True
    #找符合条件的票
    def yzgp(self,jon,gpdm,ztzt,ltsz,price):
        if self.yzbk(jon, gpdm) and self.yzdb(jon,ztzt) and self.yzltsz(jon,ltsz) and self.yzprice(jon,price):
            return True
        else:
            return False

    #验证打板条件
    def cx_yz(self,jon,gpdm,price):
        if self.yzfbzj(jon,gpdm,price) and self.zt_wfdmr(self,jon,gpdm,price) and self.cfztj(jon,gpdm,price) and self.myyd_mr(jon,gpdm) and self.mymeld_mr(jon,gpdm):
            return True
        else:
            return False
    #计算涨停价
    def zt_price(self,gpdm,price):
        if gpdm.startswith("30") or gpdm.startswith("688"):
            zt_price= round(float(price) * 1.2, 2)
            return zt_price

        if gpdm.startswith("00") or gpdm.startswith("60"):
           zt_price= round(float(price) * 1.1, 2)
           return zt_price

        if gpdm.startswith("8"):
             zt_price= round(float(price) * 1.3, 2)
             return zt_price
    #获取封板资金
    def getfbzj(self,gpdm,price):
        zt_price=self.zt_price(self, gpdm, price)
        action = "gettickdata"
        deal = DeaiClientData()
        data = deal.gettickdata(action, gpdm)
        if zt_price==data['price']:
            fbzj=int(data['bid_vol1'])*100*float(zt_price)
            fbzj=fbzj/10000
            return fbzj


    #涨停且卖一无封单
    def get_zt_my_no(self,gpdm,price):
        zt_price=self.zt_price(self, gpdm, price)
        action = "gettickdata"
        deal = DeaiClientData()
        data = deal.gettickdata(action, gpdm)
        if zt_price==data['price']:
           if data['ask_vol1']==0:
               return True
           else:
               return False
        else:
            return False

    #只剩卖一一档时买入
    def get_zt_my_yd(self, gpdm, price):
        zt_price = self.zt_price(self, gpdm, price)
        action = "gettickdata"
        deal = DeaiClientData()
        data = deal.gettickdata(action, gpdm)
        if data['ask_vol2'] == 0 and data['ask_vol1'] > 0 and data['ask_vol3'] == 0:
            return True
        else:
            return False

    # 只剩卖一卖二两档时买入
    def get_zt_my_me(self, gpdm, price):
        zt_price = self.zt_price(self, gpdm, price)
        action = "gettickdata"
        deal = DeaiClientData()
        data = deal.gettickdata(action, gpdm)
        if data['ask_vol2'] > 0 and data['ask_vol1'] > 0 and data['ask_vol3'] == 0 and data['ask_vol4'] == 0:
            return True
        else:
            return False






