import socket
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from Server.DealServerData import DealServerData
from timetask import TimeTsk
from Server.log import logger
from datetime import datetime, timedelta
import time
def receive_data(client_socket):
    # 读取长度前缀
    length_bytes = client_socket.recv(4)
    if not length_bytes:
        return None
    length = int.from_bytes(length_bytes, byteorder='big')
    buffer = bytearray()
    while len(buffer) < length:
        part = client_socket.recv(min(length - len(buffer), 4096))
        if not part:
            raise ConnectionError("连接中断")
        buffer += part
    return buffer.decode('utf-8')


def handle_client(client_socket, client_address):
    """
    处理单个客户端的请求
    """
    print(f"服务器提示：连接来自 {client_address}")
    try:
        data = receive_data(client_socket)
        print(f"server接收到客户端的数据: {data}")
        if not data:
            print(f"server提示客户端 {client_address} 已断开连接")
            return

        # 处理数据并返回
        deal = DealServerData()
        try:
            response = deal.deal_server_data(json.loads(data))
            response_with_end = json.dumps(response, ensure_ascii=False).encode('utf-8')
            # print(f"server发送到客户端的数据: {json.dumps(response, ensure_ascii=False)}")
            client_socket.sendall(response_with_end)
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()  # 必须执行！
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {data}", exc_info=True)
            response = {"status": "error", "message": "无效的JSON格式"}
        except Exception as e:
            logger.error('处理请求时发生异常', exc_info=True)
            response = {"status": "error", "message": "内部服务器错误"}
    except Exception as e:
        logger.error('tcpServer:handle_client:server处理数据时发生异常', exc_info=True)
        # 尝试发送错误响应
        error_response = json.dumps({"status": "error", "message": "服务器访问发生错误"})
        client_socket.sendall(error_response.encode('utf-8'))
        try:
            if client_socket:
                client_socket.shutdown(socket.SHUT_RDWR)  # 关键修复点
        except:
            pass
        if client_socket:
            client_socket.close()
    finally:
        try:
            if client_socket:
                client_socket.shutdown(socket.SHUT_RDWR)  # 关键修复点
        except:
            pass
        if client_socket:
            client_socket.close()  # 必须执行！


def start_server():
    server_socket=None
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '127.0.0.1'
        port = 5000
        server_socket.bind((host, port))
        server_socket.listen(100)

        print(f"服务端正在 {host}:{port} 上监听...")

        # 创建线程池，限制最多同时处理 100 个请求
        with ThreadPoolExecutor(max_workers=30) as executor:
            while True:
                try:
                    client_socket, client_address = server_socket.accept()
                    print("启动服务器连接")
                    # 将任务提交到线程池
                    executor.submit(handle_client, client_socket, client_address)
                    print(f"线程池当前活跃线程数: {executor._work_queue.qsize()}")
                except Exception as e:
                    logger.error(f"接受客户端连接时发生错误: {str(e)}", exc_info=True)
                    # 可以选择继续运行或退出
                    continue  # 继续等待新连接

    except KeyboardInterrupt:
        print("服务器正在关闭...")
    finally:
        if server_socket:
            server_socket.close()
            print("服务器已关闭")


#日线数据更新，设置定时器任务
def run_timetask():
    try:
        tik = TimeTsk()
        tik.timetask()
    except Exception as e:
        logger.error('timetask执行出错', exc_info=True)
    finally:
        # 安排下一次执行，7小时后
        timer = threading.Timer(1 * 3600, run_timetask)
        timer.daemon = True
        timer.start()


def start_timetask():
    print("start_timetask")
    tik = TimeTsk()
    # 先手动执行一次初始化
    tik.timetask()
    # 计算第一次执行时间（今天的15点）
    now = datetime.now()
    next_run = now.replace(hour=15, minute=0, second=0, microsecond=0)
    # 如果当前时间已经超过今天的15点（使用>而不是>=）
    if now > next_run:
        next_run += timedelta(days=1)  # 改为明天15点
    initial_delay = (next_run - now).total_seconds()
    # 创建第一次定时器
    timer = threading.Timer(initial_delay, run_timetask)
    timer.daemon = True
    timer.start()



if __name__ == "__main__":
    start_timetask()
    start_server()



