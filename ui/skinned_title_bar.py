from PyQt5 import QtWidgets, QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

class SkinnedTitleBar(QtWidgets.QDialog):
    "A plain, button less title bar"

    def __init__(self, parent, height, color_hex):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: " + color_hex + ";")
        self.setMinimumHeight(height)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    @QtCore.pyqtSlot()
    def close(self):
        self.parentWidget().close()

    @QtCore.pyqtSlot()
    def maximize(self):
        if self.parentWidget().windowState() == Qt.WindowMaximized:
            self.parentWidget().showNormal()
        else:
            self.parentWidget().showMaximized()

    @QtCore.pyqtSlot()
    def minimize(self):
        self.parentWidget().showMinimized()

    def mousePressEvent(self, event):
        cursor_size = QtCore.QPoint(12, 12)
        self.offset = event.pos() + cursor_size

    def mouseMoveEvent(self, event):
        self.parentWidget().move(event.globalPos() - self.offset)
