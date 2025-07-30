import sys

from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QDialog, QHBoxLayout, \
    QSpacerItem, QSizePolicy, QScrollArea, QWidget
from PySide6.QtGui import QPixmap, QIcon
import pandas as pd
import chardet
import re
import os
from PySide6.QtCore import Signal, Qt
from santou.logging.log import logger
from santou.path import path
def get_button_style():
    """Returns the style for the buttons."""
    return """
        QPushButton {
            background-color: #fd7e14;  /* 按钮背景色 */
            color: white;              /* 按钮文字颜色 */
            font-size: 15px;           /* 按钮字体大小 */
            border: none;              /* 去掉边框 */
            border-radius: 5px;        /* 圆角边框 */
        }

        QPushButton:pressed {
            background-color: #FFCCCB; /* 按下时的背景色 */
        }
    """
class FileSelectionDialog(QDialog):
    # 定义一个信号，用于传递提取到的股票代码
    stock_codes_extracted = Signal(list)

    def __init__(self,table):
        super(FileSelectionDialog, self).__init__()
        self.base_dir = path().get_base_path()  # 获取基础路径
        photo_path = os.path.join(self.base_dir,"photo", 'title_top.png')
        self.setWindowIcon(QIcon(photo_path))
        self.setWindowTitle("选择文件")
        self.setFixedSize(400, 450)  # 调整窗口大小以容纳更多内容
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.table=table
        # 添加“导入同花顺自选股说明”链接
        self.ths_link = QLabel("<a href='ths'>导入同花顺自选股说明</a>")
        self.ths_link.setFixedHeight(20)
        self.ths_link.setOpenExternalLinks(False)  # 禁用外部链接
        self.ths_link.linkActivated.connect(self.show_ths_instructions)  # 绑定点击事件
        self.layout.addWidget(self.ths_link)

        # 添加间距（100 像素）
        spacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.addItem(spacer)

        # 添加“导入通达信自选股说明”链接
        self.tdx_link = QLabel("<a href='tdx'>导入通达信自选股说明</a>")
        self.tdx_link.setFixedHeight(20)
        self.tdx_link.setOpenExternalLinks(False)  # 禁用外部链接
        self.tdx_link.linkActivated.connect(self.show_tdx_instructions)  # 绑定点击事件
        self.layout.addWidget(self.tdx_link)

        # 创建水平布局，用于放置文件选择按钮和文件路径标签
        file_layout = QHBoxLayout()

        # 创建文件选择按钮
        self.file_button = QPushButton("选择文件")
        self.file_button.setFixedSize(100, 30)
        self.file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_button)

        # 创建显示文件路径的标签
        self.file_label = QLabel("未选择文件")
        file_layout.addWidget(self.file_label)

        # 将水平布局添加到主布局中
        self.layout.addLayout(file_layout)

        # 创建确认按钮
        self.confirm_button = QPushButton("确 认")
        self.confirm_button.setStyleSheet(get_button_style())
        self.confirm_button.setFixedSize(380, 30)
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.layout.addWidget(self.confirm_button)

        # 初始化文件路径
        self.file_path = None

    def select_file(self):
        # 打开文件选择对话框，限制文件类型为 Excel 和 TXT
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("文本文件 (*.txt)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec():
            self.file_path = file_dialog.selectedFiles()[0]
            self.file_label.setText(self.file_path)

    def confirm_selection(self):
        if self.file_path:
            # 在这里处理文件内容提取逻辑
            stock_codes = self.extract_file_content()
            if stock_codes:
                # 发射信号，传递提取到的股票代码

                # 获取 ck_table 中表的行数
                current_row_count = self.table._model.rowCount()
                total_count = current_row_count + len(stock_codes)
                to=80-current_row_count
                if total_count > 80:
                    # 超过 80 条数据，提示请删除数据，不关闭窗口
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("提示")
                    msg_box.setText(f"列表中数据不能超过 80 条，请重新导入，列表中已有{current_row_count}条，导入文件中的数据不能超过{to}条！")
                    msg_box.setIcon(QMessageBox.Information)
                    ok_button = msg_box.addButton("确定", QMessageBox.AcceptRole)
                    ok_button.setStyleSheet("min-width: 60px; min-height: 25px; font-size: 14px;")
                    msg_box.exec()
                else:
                    self.stock_codes_extracted.emit(stock_codes)
                    self.accept()  # 关闭对话框

        else:
            # 自定义警告框：未选择文件
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("警告")
            msg_box.setText("请先选择一个文件！")

            # 设置按钮为 "是"，并调整按钮大小
            yes_button = msg_box.addButton("是", QMessageBox.YesRole)
            yes_button.setFixedSize(50, 30)

            msg_box.exec()

    def extract_file_content(self):
        # 根据文件类型提取内容
        if self.file_path.endswith('.xlsx') or self.file_path.endswith('.xls'):
            return self.extract_excel_content()
        elif self.file_path.endswith('.txt'):
            return self.extract_txt_content()
        return []

    def extract_txt_content(self):
        try:
            # 检测文件编码
            with open(self.file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                file_encoding = result['encoding']

            # 使用检测到的编码读取文件
            try:
                df = pd.read_csv(self.file_path, sep='\t', encoding=file_encoding)
            except Exception as e:
                # 如果检测到的编码无法读取，尝试使用常见编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'ansi']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(self.file_path, sep='\t', encoding=encoding)
                        break
                    except Exception as e:
                        continue
                else:
                    # 自定义警告框：文件编码错误
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("错误")
                    msg_box.setText("无法读取文件，文件编码可能不兼容。")

                    # 设置按钮为 "是"，并调整按钮大小
                    yes_button = msg_box.addButton("是", QMessageBox.YesRole)
                    yes_button.setFixedSize(50, 30)

                    msg_box.exec()
                    return []

            # 检查是否存在 "代码" 列
            if "代码" in df.columns:
                # 提取 "代码" 列并去除字符，只保留数字
                stock_codes = df["代码"].astype(str).tolist()
                # 使用正则表达式去除非数字字符
                stock_codes = [re.sub(r'\D', '', code) for code in stock_codes]

                return stock_codes
            else:
                # 自定义警告框：未找到 "代码" 列
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("错误")
                msg_box.setText("TXT 文件中未找到 '代码' 列！")

                # 设置按钮为 "是"，并调整按钮大小
                yes_button = msg_box.addButton("是", QMessageBox.YesRole)
                yes_button.setFixedSize(50, 30)

                msg_box.exec()
                return []
        except Exception as e:
            # 自定义警告框：读取文件失败
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"读取 TXT 文件失败: {str(e)}")

            # 设置按钮为 "是"，并调整按钮大小
            yes_button = msg_box.addButton("是", QMessageBox.YesRole)
            yes_button.setFixedSize(50, 30)

            msg_box.exec()
            return []

    def show_ths_instructions(self):
        # 获取当前脚本所在目录
        self.base_dir = path().get_base_path()  # 获取基础路径

        image_paths = [
            os.path.join(self.base_dir, 'photo', 'ths4.png'),
            os.path.join(self.base_dir, 'photo', 'ths2.png'),
            os.path.join(self.base_dir, 'photo', 'ths6.png'),
        ]
        # 弹出同花顺自选股说明界面
        self.instructions_dialog = InstructionsDialog("导入同花顺自选股说明", image_paths)
        self.instructions_dialog.exec()

    def show_tdx_instructions(self):
        # 获取当前脚本所在目录
        self.base_dir = path().get_base_path()  # 获取基础路径

        image_paths = [
            os.path.join(self.base_dir, 'photo', 'tdx1.png'),
            os.path.join(self.base_dir, 'photo', 'tdx4.png'),
            os.path.join(self.base_dir, 'photo', 'tdx3.png'),
            os.path.join(self.base_dir, 'photo', 'tdx6.png'),
        ]
        # 弹出通达信自选股说明界面
        self.instructions_dialog = InstructionsDialog("导入通达信自选股说明", image_paths)
        self.instructions_dialog.exec()


class InstructionsDialog(QDialog):
    def __init__(self, title, image_paths, parent=None):
        super(InstructionsDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.setFixedHeight(550)  # 固定对话框高度为 500
        self.setFixedWidth(450)
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建滚动区域
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)  # 允许内容调整大小

        # 创建滚动区域的内容部件
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # 添加图片
        for path in image_paths:
            image_label = QLabel(content_widget)
            pixmap = QPixmap(path)

            if pixmap.isNull():
                print(f"无法加载图片: {path}")
                continue

            # 固定宽度为 400，保持高度比例
            scaled_pixmap = pixmap.scaledToWidth(400, mode=Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)  # 图片居中显示
            content_layout.addWidget(image_label)

        # 将内容部件设置为滚动区域的部件
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button)