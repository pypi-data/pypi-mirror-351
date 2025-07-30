import logging
import os
from Server.path import path
# 创建一个日志记录器
logger = logging.getLogger(__name__)
# 设置日志级别
logger.setLevel(logging.DEBUG)

# 获取基础路径
base_path = path().get_base_path()
# 使用os.path.join构建日志目录路径
log_dir = os.path.join(base_path, 'app.log')
print(log_dir)
# 创建一个文件处理器，将日志记录到文件中，并指定编码为 UTF-8
file_handler = logging.FileHandler(log_dir, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 创建一个控制台处理器，将日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 定义日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 将处理器添加到日志记录器中
logger.addHandler(file_handler)
logger.addHandler(console_handler)