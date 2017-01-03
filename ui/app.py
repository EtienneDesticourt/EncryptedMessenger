from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtWebKitWidgets import QWebView
import os
import threading
from ui.widgets.skinned_title_bar import SkinnedTitleBar
from ui.widgets.default_dialog import DefaultDialog
from communication.contact import Contact
from ui.application import Application
from communication.network import Network
from communication.contact_manager import ContactManager
from communication.server import Server
import config

app = QApplication([])

URL = "http://localhost:5000"
network = Network(URL)

contact_manager = ContactManager()

win = DefaultDialog()
wrapper = Application(win, network, contact_manager)
win.show()
wrapper.execute()


with Server("0.0.0.0", config.PORT) as server:
    threading.Thread(target=server.listen, args=[wrapper.handle_connecting_contact])
    app.exec_()
