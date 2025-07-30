import hashlib
import subprocess
import uuid
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


class md5_jiami():
    def get_cpu_id_windows(self):
        try:
            # 执行 WMIC 命令获取 CPU 标识
            output = subprocess.check_output('wmic cpu get ProcessorId', shell=True)
            # 将输出转换为字符串并按行分割
            lines = output.decode('utf-8').split('\n')
            # 遍历每一行
            for line in lines:
                line = line.strip()
                if line and line != 'ProcessorId':
                    return line
            return None
        except Exception as e:
            print(f"获取 CPU 标识时出错: {e}")
            return None


    def get_mac_address(self):
        mac = uuid.getnode()
        mac_hex = ':'.join(("%012X" % mac)[i:i + 2] for i in range(0, 12, 2))
        return mac_hex

    def md5_encrypt(self,text):
        # 创建MD5对象
        md5 = hashlib.md5()
        # 将输入的字符串编码为字节类型
        text_bytes = text.encode('utf-8')
        # 更新MD5对象的内容
        md5.update(text_bytes)
        # 获取加密后的十六进制字符串
        encrypted_text = md5.hexdigest()

        return encrypted_text


    def get_md5(self):
        # 调用函数获取 CPU 标识
        cpu_id = self.get_cpu_id_windows()
        mac=self.get_mac_address()
        str=f"{cpu_id}-*-{mac}"
        encrypted_text1=self.md5_encrypt(str)
        encrypted_text2=self.md5_encrypt(encrypted_text1)
        #print(encrypted_text2)








