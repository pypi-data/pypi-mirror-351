
import winreg
from santou.logging.log import logger
class md5_jiami():
    def get_machine_guid(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
            value, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            return value
        except Exception as e:

            logger.error('mi:get_machine_guid:错误', exc_info=True)
            return None


    def get_md5(self):
        machine_guid = self.get_machine_guid()
        if machine_guid:
           return machine_guid
        else:
           return None








