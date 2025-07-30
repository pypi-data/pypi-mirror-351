import sys
import os

class path:
    def get_base_path(self):
        # 推荐使用更严格的判断方式
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # 打包后情况（兼容 PyInstaller 和 Nuitka）
            base_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境情况
            base_dir = os.path.dirname(os.path.abspath(__file__))
        return base_dir

