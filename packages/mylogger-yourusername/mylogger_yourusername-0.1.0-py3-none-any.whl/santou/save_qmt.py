class save_qmt(object):
    _instance = None
    save_qmt1 = {}
    save_class = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # 初始化类变量
            cls.save_qmt1 = {}
            cls.save_class = {}
        return cls._instance

    def save_tader(self, account, qmt_class):
        if account not in self.save_qmt1:
            self.save_qmt1[account] = qmt_class
            return True
        return False

    def yz_tader(self, account):
        return account in self.save_qmt1

    def get_tader(self, account):
        return self.save_qmt1.get(account)

    def save_cla(self, account, gpdm, zx_class):
        if account not in self.save_class:
            self.save_class[account] = {}

        if gpdm in self.save_class[account]:
            self.clear_class(account, gpdm)

        self.save_class[account][gpdm] = zx_class
        print(self.save_class)
    def get_class(self, account, gpdm):
        account_dict = self.save_class.get(account, {})
        return account_dict.get(gpdm)

    def clear_class(self, account, gpdm):
        if account in self.save_class:
            if gpdm in self.save_class[account]:
                self.save_class[account][gpdm].stop_operation()
                del self.save_class[account][gpdm]
                if not self.save_class[account]:
                    del self.save_class[account]
                return True
        return False