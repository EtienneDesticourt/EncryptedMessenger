from ui.widgets.skinned_title_bar import SkinnedTitleBar
from ui.widgets.web_dialog import WebDialog
from ui.widgets.borderless_window import BorderlessWindow
import logging

class DefaultDialog(BorderlessWindow, WebDialog):
    def __init__(self):
        super(DefaultDialog, self).__init__(SkinnedTitleBar,
                                            parent=self,
                                            height=20,
                                            color_hex="#1E262B")

        # # PyQt5 5.10: Objects must now be registered before page load!!
        self.add_js_object(self.title_bar, "title_bar")
        self.centralWidget = self.view
        # self.view.loadFinished.connect(self.on_load_finished)
        settings = self.view.page().settings()
        settings.ShowScrollBars  = False

        self.layout.addWidget(self.title_bar)
        self.logger = logging.getLogger(__name__)
