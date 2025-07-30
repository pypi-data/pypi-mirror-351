import socket
import json

from santou.ConfigReader import ConfigReader
from santou.logging.log import logger

class TcpClient:
    def __init__(self):
        super(TcpClient, self).__init__()
        #self.config_reader = ConfigReader()
        #self.ip, self.port = self.config_reader.read_config()

    def receive_data(self, client_socket):
        buffer = b''
        while True:
            part = client_socket.recv(2048)
            if not part:
                break
            buffer += part
        return buffer

    def start_client(self, message):
        client_socket = None
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10)  # 设置10秒超时
            client_socket.connect(("110.40.24.63", 5000))
            #client_socket.connect(("127.0.0.1", 5000))
            #print(f"客户端 已成功连接到服务端 127.0.0.1:5000{message}")

            # 发送数据
            message_bytes = json.dumps(message).encode('utf-8')
            length_prefix = len(message_bytes).to_bytes(4, byteorder='big')  # 4字节长度前缀
            client_socket.sendall(length_prefix + message_bytes)
            client_socket.shutdown(socket.SHUT_WR)
            #client_socket.sendall(utf8_encoded_str)

        except Exception as e:
            logger.error('TcpClient:start_client:发送数据时发生错误', exc_info=True)
        try:
            # 接收服务端的响应
            response = self.receive_data(client_socket)
            decoded_response = json.loads(response.decode('utf-8'))
            #print(f"decoded_response:{decoded_response}")
            #print(f"客户端 接收 服务器 数据: {decoded_response}")

            return decoded_response
        except Exception as e:
            logger.error('TcpClient:start_client:接收数据时发生错误', exc_info=True)
        finally:
            client_socket.close()
