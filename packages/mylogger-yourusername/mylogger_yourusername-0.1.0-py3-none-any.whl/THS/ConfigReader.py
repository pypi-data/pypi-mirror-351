import json
import os
import sys
from pathlib import Path
from santou.logging.log import logger

class ConfigReader:
    def __init__(self, config_path="config.json"):
        self.base_dir = self._get_base_path()
        self.config_path = os.path.join(self.base_dir, config_path)

    def _get_base_path(self):
        """动态获取当前运行环境的基础路径"""
        if getattr(sys, 'frozen', False):
            # 打包后路径（Nuitka/PyInstaller）
            return sys._MEIPASS
        else:
            # 开发环境路径（当前文件所在目录）
            return os.path.dirname(os.path.abspath(__file__))

    def read_config(self):
        """读取配置文件中的IP和端口，失败时返回默认值"""
        default_config = {"ip": "110.40.24.63", "port": 7891}
        try:
            # 检查配置文件是否存在
            if not os.path.exists(self.config_path):
                logger.error(f"配置文件 {self.config_path} 不存在")
                return default_config["ip"], default_config["port"]

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

                # 安全获取字段，避免KeyError
                ip = config.get("ip", default_config["ip"]).strip()
                port_str = str(config.get("port", default_config["port"])).strip()

                # 验证端口是否为有效整数
                try:
                    port = int(port_str)
                    if port <= 0:
                        raise ValueError("端口号必须大于0")
                except ValueError as e:
                    logger.error(f"端口号无效: {port_str}, 使用默认端口 {default_config['port']}")
                    port = default_config["port"]

                # 验证IP是否非空
                if not ip:
                    logger.error("IP地址为空，使用默认IP")
                    ip = default_config["ip"]

                print(f"成功读取配置: IP={ip}, Port={port}")
                return ip, port

        except json.JSONDecodeError as e:
            logger.error(f"配置文件解析失败: {str(e)}")
            return default_config["ip"], default_config["port"]
        except PermissionError as e:
            logger.error(f"无权限读取配置文件: {str(e)}")
            return default_config["ip"], default_config["port"]
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return default_config["ip"], default_config["port"]