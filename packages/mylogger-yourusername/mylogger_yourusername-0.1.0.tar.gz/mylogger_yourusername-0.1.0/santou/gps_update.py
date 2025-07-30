from santou.DeaiClientData import DeaiClientData


class gps_update():
    gps=[]
    def __init__(self):
       pass
        #每隔一段时间查一次
    def update(self,data):
        global  gps
        gps=data
        if len(gps)>0:
            action="update_gps"
            deal = DeaiClientData()
            self.gps = deal.update_gps(action,gps)

