from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWebKitWidgets import QWebView
from ui.widgets.skinned_title_bar import SkinnedTitleBar
from ui.widgets.dark_shadow_effect import DarkShadowEffect

class DefaultDialog(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.bindings = []
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        effect = DarkShadowEffect()
        self.setGraphicsEffect(effect)

        self.title_bar = SkinnedTitleBar(parent=self, height=20, color_hex="#1E262B")
        self.add_binding(self.title_bar, "title_bar")

        self.view = QWebView()
        self.view.loadFinished.connect(self.on_load_finished)
        main_frame = self.view.page().mainFrame()
        main_frame.setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        main_frame.setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.title_bar)
        layout.addWidget(self.view)
        layout.setSpacing(0)


    def add_binding(self, js_object, name):
        self.bindings.append((js_object, name))

    def add_js_object(self, js_object, name):
        self.view.page().mainFrame().addToJavaScriptWindowObject(name, js_object)

    def load_page(self, url):
        self.view.load(url)

    def on_load_finished(self):
        for binding in self.bindings:
            self.add_js_object(*binding)
        self.on_done_binding()

    def on_done_binding(self):
        self.view.page().mainFrame().evaluateJavaScript("fillContactList();") # TODO: Move somewhere else

