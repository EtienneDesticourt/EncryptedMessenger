from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
import json
import config

class SettingsManager(QObject):
    # Emitted when settings are loaded: run as client, peer url, port
    settings_loaded = pyqtSignal(bool, str, int)
    settings_saved = pyqtSignal()


    def __init__(self, settings_file=config.SETTINGS_FILE):
        QObject.__init__(self)
        self.settings_file = settings_file
        self._settings = {}

    @pyqtSlot()
    def load_settings(self):
        with open(self.settings_file, "r") as f:
            self._settings = json.load(f)
        self.settings_loaded.emit(self._settings["run_as_client"],
                                  self._settings["peer_registry_url"],
                                  self._settings["port"])

    @pyqtSlot(bool, str, int)
    def save_settings(self, run_as_client, peer_registry_url, port):
        self._settings["run_as_client"] = run_as_client
        self._settings["peer_registry_url"] = peer_registry_url
        self._settings["port"] = port

        with open(self.settings_file, "w") as f:
            json.dump(self._settings, f)
            
        self.settings_saved.emit()


