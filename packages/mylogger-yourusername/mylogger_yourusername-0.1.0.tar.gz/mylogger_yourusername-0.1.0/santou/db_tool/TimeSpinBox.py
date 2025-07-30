
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSpinBox, QLabel
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QValidator  # 必须导入 QValidator


class TimeSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()
        # 时间范围（以分钟为单位）
        self.min_time1 = 9 * 60 + 30  # 09:25 (565分钟)
        self.max_time1 = 11 * 60 + 30  # 11:30 (690分钟)
        self.min_time2 = 13 * 60  # 13:00 (780分钟)
        self.max_time2 = 15 * 60  # 15:00 (900分钟)

        # 设置SpinBox范围（分钟数）
        self.setRange(self.min_time1, self.max_time2)
        self.setSingleStep(5)  # 步长5分钟

    def validate(self, text, pos):
        """验证输入是否为有效的数字"""
        try:
            value = int(text)
            if self._is_time_valid(value):
                return (QValidator.State.Acceptable, text, pos)
            return (QValidator.State.Intermediate, text, pos)
        except ValueError:
            return (QValidator.State.Invalid, text, pos)

    def textFromValue(self, value):
        """将分钟数转换为 HH:mm 格式显示"""
        hours = value // 60
        minutes = value % 60
        return f"{hours:02d}:{minutes:02d}"

    def valueFromText(self, text):
        """将输入的数字转换为分钟数"""
        try:
            return int(text)
        except ValueError:
            return 0

    def stepBy(self, steps):
        """处理上下按钮的步进逻辑"""
        current = self.value()
        if steps > 0:
            # 正向步进（跳过无效区间）
            if current == self.max_time1:
                self.setValue(self.min_time2)
            elif current >= self.max_time2:
                self.setValue(self.max_time2)
            else:
                super().stepBy(steps)
        else:
            # 反向步进（跳过无效区间）
            if current == self.min_time2:
                self.setValue(self.max_time1)
            elif current <= self.min_time1:
                self.setValue(self.min_time1)
            else:
                super().stepBy(steps)

    def _is_time_valid(self, minutes):
        """检查时间是否在允许范围内"""
        return (
                (self.min_time1 <= minutes <= self.max_time1) or
                (self.min_time2 <= minutes <= self.max_time2)
        )


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("时间范围限制案例")
        layout = QVBoxLayout()

        self.spin_box = TimeSpinBox()
        self.label = QLabel()
        self.spin_box.valueChanged.connect(self.update_label)
        layout.addWidget(self.spin_box)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def update_label(self):
        minutes = self.spin_box.value()
        time = QTime(0, 0).addSecs(minutes * 60)
        self.label.setText(f"当前时间: {time.toString('HH:mm')}")


