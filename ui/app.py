from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtWebKitWidgets import QWebView
import os
from ui.skinned_title_bar import SkinnedTitleBar
from ui.default_dialog import DefaultDialog
from communication.contact import Contact


app = QApplication([])
path = os.path.join(os.getcwd(), "ui\\register.html")
path = QUrl.fromLocalFile(path)
win = DefaultDialog(path)
win.show()
app.exec_()
