from PySide6.QtWidgets import QLineEdit


class moneySeparatedLineEdit(QLineEdit):
    """自定义 QLineEdit，实现数字用逗号隔开"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.format_number)  # 绑定文本变化事件

    def format_number(self):
        """格式化输入的数字"""
        text = self.text().replace(",", "")  # 移除所有逗号
        if text == "":
            return

        try:
            # 尝试将输入内容转换为浮点数
            num = float(text)
            # 格式化数字，添加逗号
            formatted_num = "{:,.2f}".format(num) if "." in text else "{:,}".format(int(num))
            # 更新输入框内容
            self.setText(formatted_num)
        except ValueError:
            # 如果输入不是数字，清空输入框
            self.setText("")