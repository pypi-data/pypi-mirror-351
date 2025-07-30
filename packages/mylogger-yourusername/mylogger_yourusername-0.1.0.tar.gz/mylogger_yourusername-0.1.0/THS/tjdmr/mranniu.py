from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, Signal
from PySide6.QtGui import QPainter, QColor, QFont


class SwitchButton(QWidget):
    # 定义两个信号，分别在开关打开和关闭时发出
    switched_on = Signal()
    switched_off = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(110, 30)
        self._is_checked = False
        self._circle_x = 5
        self._animation = QPropertyAnimation(self, b"circle_x", self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)

    @property
    def is_checked(self):
        return self._is_checked

    @is_checked.setter
    def is_checked(self, value):
        if self._is_checked != value:
            self._is_checked = value
            self._start_animation()
            if value:
                self.switched_on.emit()
            else:
                self.switched_off.emit()
            self.update()  # 手动触发更新

    @Property(int)
    def circle_x(self):
        return self._circle_x

    @circle_x.setter
    def circle_x(self, value):
        self._circle_x = value
        self.update()  # 确保每次 circle_x 更新时，界面都会刷新

    def _start_animation(self):
        if self._is_checked:
            self._animation.setStartValue(5)
            self._animation.setEndValue(self.width() - 25)
        else:
            self._animation.setStartValue(self.width() - 25)
            self._animation.setEndValue(5)
        self._animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置背景颜色，关闭时为灰色，打开时为橘红色
        background_color = QColor(128, 128, 128) if not self._is_checked else QColor(255, 165, 0)
        painter.setBrush(background_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2)

        # 绘制圆形
        circle_color = QColor(255, 255, 255)
        painter.setBrush(circle_color)
        painter.drawEllipse(self._circle_x, 5, 20, 20)  # 确保使用 self._circle_x

        # 设置字体
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)  # 调整字体大小，可根据需要修改
        painter.setFont(font)

        # 根据开关状态修改要绘制的文本
        text = "未   买" if not self._is_checked else "买入中..."
        text_color = QColor(255, 255, 255)  # 文本颜色固定为白色
        painter.setPen(text_color)
        text_rect = self.rect()
        painter.drawText(text_rect, Qt.AlignCenter, text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_checked = not self.is_checked
            self.update()