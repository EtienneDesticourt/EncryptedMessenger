from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView 
from  PyQt5.QtWebChannel import QWebChannel
from ui.widgets.skinned_title_bar import SkinnedTitleBar
from ui.widgets.web_dialog import WebDialog
from ui.widgets.borderless_window import BorderlessWindow
# from ui.widgets.dark_shadow_effect import DarkShadowEffect
import logging

class DefaultDialog(BorderlessWindow, WebDialog, QMainWindow):
    def __init__(self):
        super(DefaultDialog, self).__init__(SkinnedTitleBar,
                                            parent=self,
                                            height=20,
                                            color_hex="#1E262B")
        # BorderlessWindow.__init__(self, SkinnedTitleBar,
        #                           parent=self,
        #                           height=20,
        #                           color_hex="#1E262B")
        print("starting")

        # # PyQt5 5.10: Objects must now be registered before page load!!
        self.add_js_object(self.title_bar, "title_bar")
        self.centralWidget = self.view
        # self.view.loadFinished.connect(self.on_load_finished)
        settings = self.view.page().settings()
        settings.ShowScrollBars  = False

        self.layout.addWidget(self.title_bar)
        self.logger = logging.getLogger(__name__)