from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget
from ui.widgets.web_dialog import WebDialog
import threading
import logging
import sys


class NotificationDialog(QWidget, WebDialog):
    popuphidden = QtCore.pyqtSignal()

    def __init__(self, name, text, size,
                 visible_time=5000,
                 fade_time=800):
        super(NotificationDialog, self).__init__()
        self.name = name
        self.text = text
        self.visible_time = visible_time
        self.fade_time = fade_time

        self.setWindowFlags(QtCore.Qt.SplashScreen |
                            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumSize(QtCore.QSize(300, 100))

        self.animation = QtCore.QPropertyAnimation(
            self, b"windowOpacity", self)
        self.animation.finished.connect(self.hide)

        self.timer = threading.Timer(
            self.visible_time / 1000, self.hide_animation)
        # self.timer = QtCore.QTimer(self)
        # self.timer.timeout.connect(self.hide_animation)
        # self.popuphidden.connect(self.close)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.resize(*size)
        self.move_to_bottom()
        self.load_page("ui\\html\\notification.html")
        # self.view.setMouseTracking(True)
        # self.setMouseTracking(True)

        # qApp.installEventFilter(self)

        self.view.loadFinished.connect(self.set_content)

        # self.add_js_object(self, "wrapper")

    def set_content(self):
        js_function = """
        userName = document.getElementById('username');
        userName.innerText = '%s';
        message = document.getElementById('message');
        message.innerText = '%s';
        """
        self.evaluate_js(js_function % (self.name, self.text))

    def click_callback(self):
        self.close()

    # def eventFilter(self, obj, event):
    #     if event.type() == QEvent.MouseButtonRelease:
    #         self.click_callback()
    #     return super(NotificationDialog, self).eventFilter(obj, event)

    def show(self):
        self.setWindowOpacity(0.0)
        self.animation.setDuration(self.fade_time)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        QtWidgets.QWidget.show(self)
        self.animation.start()
        self.timer.start()
        # self.set_content()

    def hide_animation(self):
        # self.timer.stop()
        self.animation.setDuration(self.fade_time)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()

    def hide(self):
        if self.windowOpacity() == 0:
            QtWidgets.QWidget.hide(self)
            self.popuphidden.emit()

    def move_to_bottom(self):
        screen_geometry = QtWidgets.QApplication.desktop().availableGeometry()
        screen_size = (screen_geometry.width(), screen_geometry.height())
        win_size = (self.frameSize().width(), self.frameSize().height())
        x = screen_size[0] - win_size[0] - 10
        y = screen_size[1] - win_size[1] - 10
        self.move(x, y)
