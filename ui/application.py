from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from communication.network import Network
import os


class Application(QObject):

    def __init__(self, main_dialog, network, contact_manager):
        QObject.__init__(self)
        self.main_dialog = main_dialog
        self.network = network
        self.contact_manager = contact_manager
        self.main_dialog.add_binding(self, "wrapper")

    def build_qurl(self, local_file):
        path = os.path.join(os.getcwd(), local_file)
        path = QUrl.fromLocalFile(path)
        return path

    def execute(self):
        try:
            with open(".user", "r") as f:
                self.username = f.read()
                self.load_index()
        except FileNotFoundError:
            self.load_register()

    @pyqtSlot(str, result=str)
    def register(self, username):
        if not self.network.has_peer(username):
            success, message = self.network.register(username)
            if success:
                with open(".user", "w") as f:
                    f.write(username)
                    self.username = username
            return message
        else:
            return "There is already a user with that name."

    @pyqtSlot(str, result=str)
    def connect(self, username):
        response = self.network.connect(username)

    @pyqtSlot(result=int)
    def get_num_contacts(self):
        return len(self.contact_manager.contacts)

    @pyqtSlot(int, result=str)
    def get_contact_name(self, index):
        return self.contact_manager.contacts[index].name

    @pyqtSlot()
    def load_index(self):
        print("called")
        self.connect(self.username)
        print("connected")
        self.contact_manager.load_contacts()
        print("contacts loaded")
        path = self.build_qurl("ui\\index.html")
        print("loading index")
        self.main_dialog.load_page(path)

    @pyqtSlot()
    def load_register(self):
        path = self.build_qurl("ui\\register.html")
        self.main_dialog.load_page(path)

    @pyqtSlot(str)
    def debug_print(self, message):
        print(message)
