from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect
import os
import threading
import time
from ui.widgets.skinned_title_bar import SkinnedTitleBar
from ui.widgets.default_dialog import DefaultDialog
from communication.contact import Contact
from ui.application import Application
from communication.network import Network
from communication.contact_manager import ContactManager
from communication.server import Server
import config
import logging
import logging.config
from tests.communication.network_mock import MockNetwork
from ui.settings_manager import SettingsManager


logging.config.fileConfig("logging.conf")

logger = logging.getLogger(__name__)
logger.info("Starting main program.")


settings = SettingsManager()
settings.load_settings()

app = QApplication([])

# network = Network(config.PEER_REGISTRY_URL)
network = MockNetwork("")

win = DefaultDialog()
wrapper = Application(win, network, settings)
win.set_borderless_style()
win.show()
wrapper.start()

with Server("localhost", wrapper.settings_manager._settings["port"]) as server:
    threading.Thread(target=server.listen, args=[wrapper.handle_connecting_contact]).start()
    app.exec_()
for contact in wrapper.contact_manager.contacts:
    contact.stop_messenger()

time.sleep(1)
logger.info("Ending main program.")
logger.info("--------------------")
