from decimal import Decimal, ROUND_HALF_UP
class yzTool():
    #验证板块
    def yz_bk(self,jon,gpdm):
        for item in jon['bk']:
            if item=="主板":
               if gpdm.startswith('00') or gpdm.startswith('60'):
                   return True
            if item=="创业板和科创板":
                if gpdm.startswith('30') or gpdm.startswith('688'):
                   # print(f"创业板:{gpdm}")
                    return True
            if item == "北交所":  # 添加对北交所的判断
                if gpdm.startswith('8'):
                    return True



    #验证流通市值
    def yz_ltsz(self,jon,ltsz):
        ltsz=float(ltsz)

        if "ltsz_min" in jon and "ltsz_max" in jon:
            if float(jon['ltsz_min'].strip())<=ltsz and float(jon['ltsz_max'].strip())>=ltsz:
                return True
            else:
                return False
        if "ltsz_min" in jon and "ltsz_max" not in jon:
            if float(jon['ltsz_min'].strip()) <= ltsz:
                return True
            else:
                return False
        if "ltsz_min" not in jon and "ltsz_max"  in jon:
            if float(jon['ltsz_max'].strip()) >= ltsz:
                return True
            else:
                return False
        if "ltsz_min" not in jon and "ltsz_max" not in jon:
            return True



    #验证价格
    def yz_price(self,jon,price):
        price = float(price)
        if "price_min" in jon and "price_max" in jon:
            if float(jon['price_min'].strip()) <= price and float(jon['price_max'].strip()) >= price:
                return True
            else:
                return False
        if "price_min" in jon and "price_max" not in jon:
            if float(jon['price_min'].strip()) <= price:
                return True
            else:
                return False
        if "price_min" not in jon and "price_max" in jon:
            if float(jon['price_max'].strip()) >= price:
                return True
            else:
                return False
        if "price_min" not in jon and "price_max" not in jon:
            return True

    def yz_hsl(self,jon,hsl):
        # 检查 hsl 是否为空字符串
        if hsl.strip() == '':
            return True
        hsl =float(hsl.strip('%')) / 100
        if "hsl_min" in jon and "hsl_max" in jon:
            if float(jon['hsl_min'].strip()) <= hsl and float(jon['hsl_max'].strip()) >= hsl:
                return True
            else:
                return False
        if "hsl_min" in jon and "hsl_max" not in jon:
            if float(jon['hsl_min'].strip()) <= hsl:
                return True
            else:
                return False
        if "hsl_min" not in jon and "hsl_max" in jon:
            if float(jon['hsl_max'].strip()) >= hsl:
                return True
            else:
                return False
        if "hsl_min" not in jon and "hsl_max" not in jon:
            return True

    #找符合条件的票
    def yz_gp(self,jon,gpdm,ztzt,ltsz,price,hsl):
        if self.yz_bk(jon, gpdm)  and self.yz_ltsz(jon,ltsz) and self.yz_price(jon,price) and self.yz_hsl(jon,hsl):
            return True
        else:
            return False



    #计算涨停价
    def zt_price(self, gpdm, price):
        price_dec = Decimal(str(price))
        if gpdm.startswith(('300', '301', '688')):
            zt = price_dec * Decimal('1.20')
        elif gpdm.startswith(('00', '60')):
            zt = price_dec * Decimal('1.10')
        elif gpdm.startswith(('8', '4')):
            zt = price_dec * Decimal('1.30')
        return float(zt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))













