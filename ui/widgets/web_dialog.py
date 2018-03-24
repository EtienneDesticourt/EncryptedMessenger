from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
import logging
import os
from PyQt5.QtCore import QUrl


class WebDialog(QWidget):

    def __init__(self, parent=None):
        super(WebDialog, self).__init__(parent=parent)
        self.view = QWebEngineView()
        self.view.setParent(self)

        # Create com channel to share python wrappers with JS
        self.js_com_channel = QWebChannel()
        self.js_com_channel.setParent(self)

        self.view.page().setWebChannel(self.js_com_channel)

        layout = QVBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(self.view)
        layout.setSpacing(0)
        self.layout = layout
        self.layout.setParent(self)

        self.logger = logging.getLogger(__name__)

    def add_js_object(self, js_object, name):
        self.js_com_channel.registerObject(name, js_object)

    def evaluate_js(self, js):
        self.view.page().runJavaScript(js)

    def load_page(self, url):
        url = self.build_qurl(url)
        self.logger.info("Loading page %s.", url.path())
        self.view.load(url)

    def build_qurl(self, local_file):
        path = os.path.join(os.getcwd(), local_file)
        path = QUrl.fromLocalFile(path)
        return path
