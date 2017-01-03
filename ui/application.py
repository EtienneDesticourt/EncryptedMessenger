from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from communication.network import Network
from communication.network_exception import UserDoesNotExistError
from communication.server import Server
from communication.socket_manager import SocketManager
import os
import threading
import config

class Application(QObject):

    def __init__(self, main_dialog, network, contact_manager):
        QObject.__init__(self)
        self.main_dialog = main_dialog
        self.network = network
        self.contact_manager = contact_manager
        self.main_dialog.add_binding(self, "wrapper")

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
        self.connect(self.username)

    def build_qurl(self, local_file):
        path = os.path.join(os.getcwd(), local_file)
        path = QUrl.fromLocalFile(path)
        return path

    def handle_connecting_contact(self, socket, ip):
        for contact in self.contact_manager.contacts:
            contact_ip = self.network.get_peer_ip(contact.name)
            if contact_ip == ip:
                contact.has_connected(socket)
                break

    def launch_server(self):
        with Server("0.0.0.0", config.PORT) as server:
            server.listen(self.handle_connecting_contact)

    def execute(self):
        try:
            with open(".user", "r") as f:
                self.username = f.read()
                self.load_index()
        except FileNotFoundError:
            self.load_register()

    @pyqtSlot(str, result=str)
    def add_friend(self, username):
        try:
            info = self.network.get_peer_info(username)
            self.contact_manager.add_contact(info)
            return "OK"
        except UserDoesNotExistError:
            return "There is no user with that name."

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
        response = self.network.connect(username)  # TODO: Handle errors
        self.contact_manager.load_contacts(username)
        self.contact_manager.connect_to_contacts()

    @pyqtSlot(result=int)
    def get_num_contacts(self):
        return len(self.contact_manager.contacts)

    @pyqtSlot(int, result=str)
    def get_contact_name(self, index):
        return self.contact_manager.contacts[index].name

    @pyqtSlot()
    def load_index(self):
        path = self.build_qurl("ui\\index.html")
        self.main_dialog.load_page(path)

    @pyqtSlot()
    def load_register(self):
        path = self.build_qurl("ui\\register.html")
        self.main_dialog.load_page(path)

    @pyqtSlot(str)
    def debug_print(self, message):
        print(message)
