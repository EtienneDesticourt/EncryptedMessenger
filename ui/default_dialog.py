from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWebKitWidgets import QWebView
from ui.skinned_title_bar import SkinnedTitleBar
from ui.dark_shadow_effect import DarkShadowEffect

class DefaultDialog(QWidget):
    def __init__(self, path):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        effect = DarkShadowEffect()
        self.setGraphicsEffect(effect)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.view = QWebView()
        self.view.load(path)
        main_frame = self.view.page().mainFrame()
        main_frame.setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        main_frame.setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)

        title_bar = SkinnedTitleBar(parent=self, height=20, color_hex="#1E262B")
        layout.addWidget(title_bar)
        layout.addWidget(self.view)
        layout.setSpacing(0)

        main_frame.addToJavaScriptWindowObject('title_bar', title_bar)

