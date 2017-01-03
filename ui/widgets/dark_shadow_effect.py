from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5 import QtGui

class DarkShadowEffect(QGraphicsDropShadowEffect):
    def __init__(self):
        QGraphicsDropShadowEffect.__init__(self)
        self.setBlurRadius(10)
        self.setColor(QtGui.QColor(0,0,0,180))
        self.setOffset(2, 2)
