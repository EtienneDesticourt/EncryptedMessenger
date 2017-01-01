from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtWebKitWidgets import QWebView
import os
from ui.skinned_title_bar import SkinnedTitleBar
from ui.default_dialog import DefaultDialog
from communication.contact import Contact
from ui.application import Application
from communication.network import Network
from communication.contact_manager import ContactManager

app = QApplication([])

URL = "http://localhost:5000"
network = Network(URL)

contact_manager = ContactManager()

win = DefaultDialog()
wrapper = Application(win, network, contact_manager)
win.show()
wrapper.execute()


app.exec_()
