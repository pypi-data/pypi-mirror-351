from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, Signal
from PySide6.QtGui import QPainter, QColor


class LittleSwitchButton(QWidget):
    switched_on = Signal()
    switched_off = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 15)
        self._is_checked = False
        self._circle_x = 2  # 关闭状态的初始位置
        self._animation = QPropertyAnimation(self, b"circle_x", self)
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        self._enabled = True  # 新增属性，控制按钮是否可操作

    @property
    def is_checked(self):
        return self._is_checked

    @is_checked.setter
    def is_checked(self, value):
        if self._is_checked != value and self._enabled:
            self._is_checked = value
            if self._animation.state() == QPropertyAnimation.Running:
                self._animation.stop()
            self._start_animation()
            if value:
                self.switched_on.emit()
            else:
                self.switched_off.emit()

    @Property(int)
    def circle_x(self):
        return self._circle_x

    @circle_x.setter
    def circle_x(self, value):
        self._circle_x = value
        self.update()

    def _start_animation(self):
        target_x = self.width() - 13 if self._is_checked else 2
        self._animation.setStartValue(self._circle_x)
        self._animation.setEndValue(target_x)
        self._animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 不区分启用和禁用状态，只根据开关状态设置背景颜色
        bg_color = QColor(253, 126, 20) if self._is_checked else QColor(128, 128, 128)
        painter.setBrush(bg_color)
        # 去除边框绘制，只填充背景
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2)
        # 不区分启用和禁用状态，统一设置圆圈颜色
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(self._circle_x, 2, 11, 11)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._enabled:
            self.is_checked = not self.is_checked

    def setEnabled(self, enabled):
        if self._enabled == enabled:
            return
        self._enabled = enabled
        if not self._enabled:
            # 禁用时停止动画并确保位置正确
            if self._animation.state() == QPropertyAnimation.Running:
                self._animation.stop()
            self._circle_x = self.width() - 13 if self._is_checked else 2
            self.update()
        else:
            # 启用时根据状态重新启动动画
            self._start_animation()

    def isEnabled(self):
        return self._enabled
