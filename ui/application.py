from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from communication.network import Network
from communication.network_exception import NetworkException
from communication.network_exception import UserDoesNotExistError
from communication.server import Server
from communication.socket_manager import SocketManager
import os
import threading
import logging
import config


class Application(QObject):

    def __init__(self, main_dialog, network, contact_manager):
        QObject.__init__(self)
        self.main_dialog = main_dialog
        self.network = network
        self.contact_manager = contact_manager
        self.main_dialog.add_binding(self, "wrapper")
        self.active_contact_name = None
        self.logger = logging.getLogger(__name__)

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self.logger.info("Changed user to %s.", value)
        self._username = value
        self.connect(self.username)
        self.load_index()

    def build_qurl(self, local_file):
        path = os.path.join(os.getcwd(), local_file)
        path = QUrl.fromLocalFile(path)
        return path

    def handle_connecting_contact(self, socket, ip):
        self.logger.info("New contact trying to connect from ip %s.", ip)
        found_contact = False
        for contact in self.contact_manager.contacts:
            try:
                contact_ip = self.network.get_peer_ip(contact.name)
            except Exception:
                self.logger.error("There was an error while trying to fetch the ip for %s.", contact.name, exc_info=True)
                continue

            if contact_ip == ip:
                self.logger.info("Found contact %s for ip %s.", contact.name, ip)
                found_contact = True
                contact.has_connected(socket)
                break

        if not found_contact:
            self.logger.info("No contact found for ip %s.", ip)
            with SocketManager(socket):
                pass

    def launch_server(self):
        with Server("0.0.0.0", config.PORT) as server:
            server.listen(self.handle_connecting_contact)

    def execute(self):
        try:
            with open(config.USER_FILE, "r") as f:
                self.username = f.read()
        except FileNotFoundError:
            self.logger.info("No user file.")
            self.load_register()

    @pyqtSlot(str)
    def load_contact_page(self, contact_name):
        found = False
        for contact in self.contact_manager.contacts:
            if contact.name == contact_name:
                found = True
                break

        if not found:
            return
        if not contact.messenger:
            return

        self.active_contact = contact
        if contact.connected:
            self.main_dialog.evaluate_js("addNewMessages();")
        else:
            self.main_dialog.evaluate_js("addNotConnectedMessage();")

    @pyqtSlot(str, result=str)
    def add_friend(self, username):
        self.logger.info("Attempting to add contact %s.", username)
        try:
            info = self.network.get_peer_info(username)
            self.contact_manager.add_contact(self.username, info)
            return "OK"
        except UserDoesNotExistError:
            return "There is no user with that name."
        except NetworkException:
            self.logger.error("There was a problem during a request to the peer registry.", exc_info=True)
            return "There was a network exception."

    @pyqtSlot(str, result=str)
    def register(self, username):
        self.logger.info("Attempting to register as %s.", username)
        try:
            peer_exists = self.network.has_peer(username)
            if not peer_exists:
                success, message = self.network.register(username)
                if success:
                    with open(config.USER_FILE, "w") as f:
                        f.write(username)
                        self.username = username
                return message
            else:
                return "There is already a user with that name."

        except NetworkException:
            self.logger.error("There was a problem during a request to the peer registry.", exc_info=True)
            return "There was a network exception during the registration process."

        except Exception:
            self.logger.critical("There was a problem while attempting to register a new user under id %s.", username, exc_info=True)
            return "There was a critical error during the registration process."

    @pyqtSlot(str, result=str)
    def connect(self, username):
        try:
            response = self.network.connect(username)
        except NetworkException:
            # TODO: show error page
            self.logger.critical("There was a problem during a request to the peer registry.", exc_info=True)
            return
        except Exception:
            # TODO: show error page
            self.logger.critical("There was an unexpected exception.", exc_info=True)
            return

        self.contact_manager.load_contacts(username)
        for contact in self.contact_manager.contacts:
            try:
                contact.ip = self.network.get_peer_ip(contact.name)
            except Exception:
                self.logger.error("Unable to fetch ip for contact %s.", contact.name, exc_info=True)

        self.contact_manager.connect_to_contacts()

        def create_callback(contact):
            def callback(messenger):
                if contact.name == self.active_contact.name:
                    self.main_dialog.evaluateJavaScript("addNewMessages();")
                else:
                    # TODO: new message indicator
                    pass
            return callback

        for contact in self.contact_manager.contacts:
            if contact.messenger:
                callback = create_callback(contact)
                contact.messenger.set_messenger_callback(callback)

    @pyqtSlot(str)
    def post_message(self, message):
        if self.active_contact.connected:
            self.active_contact.messenger.send(message.encode('utf8') + b"\x00")

    @pyqtSlot(result=int)
    def get_num_contacts(self):
        return len(self.contact_manager.contacts)

    @pyqtSlot(int, result=str)
    def get_contact_name(self, index):
        return self.contact_manager.contacts[index].name

    @pyqtSlot(result=str)
    def get_active_contact_name(self):
        return self.active_contact.name

    @pyqtSlot(result=int)
    def get_active_contact_num_messages(self):
        return self.active_contact.messenger.num_pending_messages()

    @pyqtSlot(result=str)
    def get_active_contact_latest_message(self):
        return self.active_contact.messenger.consume_message()

    @pyqtSlot()
    def load_index(self):
        path = self.build_qurl("ui\\html\\index.html")
        self.main_dialog.load_page(path)

    @pyqtSlot()
    def load_register(self):
        path = self.build_qurl("ui\\html\\register.html")
        self.main_dialog.load_page(path)

    @pyqtSlot(str)
    def debug_print(self, message):
        print(message)
