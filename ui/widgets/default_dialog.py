from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView 
from  PyQt5.QtWebChannel import QWebChannel
from ui.widgets.skinned_title_bar import SkinnedTitleBar
from ui.widgets.borderless_window import BorderlessWindow
from ui.widgets.dark_shadow_effect import DarkShadowEffect
import logging
import ctypes.wintypes
import ctypes
import struct
import win32con
import win32gui


class DefaultDialog(BorderlessWindow):
    def __init__(self):
        BorderlessWindow.__init__(self, SkinnedTitleBar,
                                  parent=self,
                                  height=20,
                                  color_hex="#1E262B")

        # effect = DarkShadowEffect()
        # self.setGraphicsEffect(effect)


        self.view = QWebEngineView()

        # Create com channel to share python wrappers with JS
        self.js_com_channel = QWebChannel()
        self.view.page().setWebChannel(self.js_com_channel)

        # Add title bar wrapper
        # # PyQt5 5.10: Objects must now be registered before page load!!
        self.add_js_object(self.title_bar, "title_bar")

        self.view.loadFinished.connect(self.on_load_finished)
        settings = self.view.page().settings()
        settings.ShowScrollBars  = False

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.title_bar)
        layout.addWidget(self.view)
        layout.setSpacing(0)

        self.count = 0
        self.logger = logging.getLogger(__name__)

    def add_js_object(self, js_object, name):
        self.js_com_channel.registerObject(name, js_object)

    def evaluate_js(self, js):
        self.view.page().runJavaScript(js)
        # self.view.page().mainFrame().evaluateJavaScript(js)

    def load_page(self, url):
        self.logger.info("Loading page %s.", url.path())
        self.view.load(url)

    def on_load_finished(self):
        self.view.page().runJavaScript("fillContactList();")
