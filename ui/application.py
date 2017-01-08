from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from communication.network import Network
from communication.network_exception import NetworkException
from communication.network_exception import UserDoesNotExistError
from communication.contact_manager import ContactManager
from communication.server import Server
from communication.socket_manager import SocketManager
from user import User
import os
import threading
import logging
import config


class Application(QObject):

    def __init__(self, main_dialog, network, ContactManager=ContactManager):
        QObject.__init__(self)
        self.main_dialog = main_dialog
        self.network = network
        self.contact_manager = ContactManager(network)
        self.main_dialog.add_binding(self, "wrapper")
        self.active_contact_name = None
        self.user = None
        self.logger = logging.getLogger(__name__)

    def start(self):
        try:
            with open(config.USER_FILE, "r") as f:
                username = f.read()
            self.user = User(username, self.network, self.contact_manager)
            self.connect()
            self.load_index()
        except FileNotFoundError:
            self.logger.info("No user file.")
            self.load_register()

    @pyqtSlot(str, result=str)
    def register(self, username):
        try:
            username_taken = self.network.has_peer(username)
            if username_taken:
                return "There is already a user with that name."

            self.user = User(username, self.network, self.contact_manager)
            self.user.register()
            return "OK"

        except NetworkException:
            self.logger.error("There was a problem during a request to the peer registry.", exc_info=True)
            return "There was a network exception during the registration process."

        except Exception:
            self.logger.critical("There was a problem while attempting to register a new user under id %s.", username, exc_info=True)
            return "There was a critical error during the registration process."

    @pyqtSlot(result=str)
    def connect(self):
        try:
            self.user.connect()
        except NetworkException:
            # TODO: show error page
            self.logger.critical("There was a problem during a request to the peer registry.", exc_info=True)
            return
        except Exception:
            # TODO: show error page
            self.logger.critical("There was an unexpected exception.", exc_info=True)
            return

    @pyqtSlot(str)
    def activate_contact(self, name):
        self.user.set_active_contact(name)
        if self.user.active_contact.connected:
            self.main_dialog.evaluate_js("addNewMessages();")
        else:
            self.main_dialog.evaluate_js("addNotConnectedMessage();")

    @pyqtSlot(str, result=str)
    def add_friend(self, username):
        self.logger.info("Attempting to add contact %s.", username)
        try:
            self.user.add_contact(username)
            return "OK"
        except UserDoesNotExistError:
            return "There is no user with that name."
        except NetworkException:
            self.logger.error("There was a problem during a request to the peer registry.", exc_info=True)
            return "There was a network exception."

    def handle_connecting_contact(self, socket, ip):
        try:
            self.contact_manager.contact_connected(socket, ip)
        except Exception:
            self.logger.error("There was an error while trying to handle an incoming connection from ip %s with socket %s.", ip, socket, exc_info=True)
            self.display_error_notification()
        SocketManager.close(socket)


    @pyqtSlot()
    def display_online_notification(self):
        print("Went online")

    @pyqtSlot()
    def display_offline_notification(self):
        print("Went offline")

    def display_error_notification(self):
        pass

    @pyqtSlot(str)
    def post_message(self, message):
        try:
            self.user.say(message)
        except Exception:
            self.logger.critical("There was an error while posting message.", exc_info=True)

    @pyqtSlot(str, result=bool)
    def is_online(self, name):
        return self.contact_manager.get_contact(name).connected

    @pyqtSlot(result=int)
    def get_num_contacts(self):
        return len(self.contact_manager.contacts)

    @pyqtSlot(int, result=str)
    def get_contact_name(self, index):
        return self.contact_manager.contacts[index].name

    @pyqtSlot(result=str)
    def get_active_contact_name(self):
        if self.user and self.user.active_contact:
            return self.user.active_contact.name

    @pyqtSlot(result=int)
    def get_active_contact_num_messages(self):
        if self.user and self.user.active_contact:
            return self.user.active_contact.messenger.num_pending_messages()
        return 0

    @pyqtSlot(result=str)
    def get_active_contact_latest_message(self):
        try:
            return self.user.active_contact.messenger.consume_message()
        except Exception:
            pass

    @pyqtSlot(result=str)
    def get_username(self):
        if self.user:
            return self.user.username

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

    def build_qurl(self, local_file):
        path = os.path.join(os.getcwd(), local_file)
        path = QUrl.fromLocalFile(path)
        return path
