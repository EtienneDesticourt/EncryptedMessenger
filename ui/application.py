from PyQt5.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal, QVariant, pyqtProperty
from PyQt5 import QtCore
from communication.network import Network
from communication.exceptions import NetworkException
from communication.exceptions import UserDoesNotExistError
from communication.contact_manager import ContactManager
from communication.server import Server
from communication.socket_manager import SocketManager
# from ui.widgets.notification_dialog import NotificationDialog
from user import User
import os
import threading
import logging
import config

class Application(QObject):
    # Impromptu events after page load
    contact_added        = pyqtSignal()
    contact_loaded       = pyqtSignal(str)
    contact_connected    = pyqtSignal(str)
    contact_disconnected = pyqtSignal(str)
    message_received     = pyqtSignal(str, str)
    topl_error_raised    = pyqtSignal()

    # Emitted on end of page load
    user_connected       = pyqtSignal(str)
    connected_to_contact = pyqtSignal(str)
    user_registered      = pyqtSignal()

    def __init__(self, main_dialog, network, settings, ContactManager=ContactManager):
        QObject.__init__(self)
        self.main_dialog = main_dialog
        self.network = network
        self.contact_manager = ContactManager(network,
                                              connection_callback=self.on_contact_status_changed,
                                              message_callback=self.on_message_received)
        self.settings_manager = settings
        self.main_dialog.add_js_object(self, "wrapper")
        self.main_dialog.add_js_object(self.settings_manager, "settings")
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

    def on_contact_status_changed(self, contact, connected):
        if connected:
            # TODO: Remove hardcoded
            # notif = NotificationDialog(contact.name, "%s has connected." % contact.name, (100, 100))
            # notif.show()
            self.contact_connected.emit(contact.name)
        else:
            self.contact_disconnected.emit(contact.name)

    def on_message_received(self, contact, message):
        if self.main_dialog.windowState() & QtCore.Qt.WindowMinimized:
            # TODO: Remove hardcoded
            # notif = NotificationDialog("name", "message", (100, 100))
            # self.notifs.append(notif)
            # notif.show()
            pass
        elif not self.main_dialog.hasFocus():
            self.main_dialog.flash_taskbar_icon()

        self.message_received.emit(contact.name, message.decode('utf8'))

    @pyqtSlot()
    def on_callbacks_defined(self):
        # We reemit all events that might have been missed while the callbacks were being defined
        self.user_connected.emit(self.user.username)
        for contact in self.contact_manager.contacts:
            self.contact_loaded.emit(contact.name)
            if contact.connected:
                self.connected_to_contact.emit(contact.name)
        self.settings_manager.load_settings()


    @pyqtSlot(str, result=str)
    def register(self, username):
        try:
            username_taken = self.network.has_peer(username)
            if username_taken:
                return "There is already a user with that name."

            self.user = User(username, self.network, self.contact_manager)
            self.user.register()
            self.user_registered.emit(username)
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

    @pyqtSlot(str)
    def add_friend(self, username):
        self.logger.info("Attempting to add contact %s.", username)
        try:
            # Need to emit contact_added first because
            # add_contact will connect directly
            self.contact_added.emit()
            # TODO SEPARATE ADD AND CONNECT
            self.user.add_contact(username)
        except UserDoesNotExistError:
            # TODO: emit error signal
            # return "There is no user with that name."
            pass
        except NetworkException:
            # TODO: emit error signal
            self.logger.error("There was a problem during a request to the peer registry.", exc_info=True)
            # return "There was a network exception."

    def handle_connecting_contact(self, socket, ip):
        try:
            self.contact_manager.contact_connected(socket, ip)
        except Exception:
            self.logger.error("There was an error while trying to handle an incoming connection from ip %s with socket %s.", ip, socket, exc_info=True)
            self.display_error_notification()
        SocketManager.close(socket) # TODO: Indent? Closing is done in contact_connected


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
        print("heyo")
        return "thisisastring"
        if self.user:
            return QObject(self.user.username)
        return QObject("No user loaded.")

    @pyqtSlot()
    # TODO: REMOVE-> MOVED TO WEB DIALOG
    def load_index(self):
        path = "ui\\html\\index.html"
        self.main_dialog.load_page(path)

    @pyqtSlot()
    # TODO: REMOVE-> MOVED TO WEB DIALOG
    def load_register(self):
        path = "ui\\html\\register.html"
        self.main_dialog.load_page(path)

    @pyqtSlot(str)
    def debug_print(self, message):
        print(message)        
