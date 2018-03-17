# TODO: Add conditional imports (linux compat)
import win32gui
import win32api
import win32con
from win32con import GWL_STYLE, WS_POPUP, WS_THICKFRAME
from win32con import WS_CAPTION, WS_SYSMENU, WS_MAXIMIZEBOX
from win32con import WS_MINIMIZEBOX
import ctypes
import ctypes.wintypes
import struct
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from ui.widgets.exceptions import NoWindowHandleError, DWMAPIException


SM_CXPADDEDBORDER = 92
GET_X_LPARAM = lambda p: p & 0xffff
GET_Y_LPARAM = lambda p: p >> 16


class BorderlessWindow(QWidget):
    """A QT window that overrides the default Windows border style and commands.
    This allows the user to customize the title bar's style and behaviour.

    Args:
        TitleBar: An object that defines custom title bar behaviour such as close, minimize, maximize, etc...
    """
    AERO_STYLE = WS_POPUP | WS_THICKFRAME | WS_CAPTION | WS_SYSMENU | WS_MAXIMIZEBOX | WS_MINIMIZEBOX

    def __init__(self, TitleBar, *args, **kwargs):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.title_bar = TitleBar(*args, **kwargs)

    def load_dwm_api(self):
        """Loads the windows Desktop Window Manager API.

        Returns:
            An instance of the API.

        # TODO: Add raises.
        """
        dwm_api = ctypes.windll.LoadLibrary("dwmapi")
        return dwm_api

    def get_window_handle(self):
        """Gets the current window's handle.

        Returns:
            The handle as an int.

        Raises:
            NoWindowHandleError: If the handle hasn't been created yet.
        """
        hwnd_pointer = self.winId()
        try:
            hwnd = int(hwnd_pointer)
        except TypeError:
            raise NoWindowHandleError("The window doesn't have a handle yet.")
        return hwnd

    # TODO~: Transform into property if we ever decide to enable it from here.
    def is_composition_enabled(self):
        try:
            dwm_api = self.load_dwm_api()
            enabled = ctypes.c_bool()
            failure = dwm_api.DwmIsCompositionEnabled(ctypes.byref(enabled))
            enabled = enabled.value and not failure
        except AttributeError:
            raise DWMAPIException("Failed to retrieve status of DWM composition.")
        return enabled

    def set_style(self, style):
        """Sets the window's style and redraws it.

        Args:
            style: A bitmask of window style flags.
        """
        hwnd = self.get_window_handle()
        win32gui.SetWindowLong(hwnd, GWL_STYLE, style)
        self.show()

    def set_borderless_style(self):
        self.set_style(self.AERO_STYLE)

    def nativeEvent(self, eventType, message):
        msg = ctypes.wintypes.MSG.from_address(message.__int__())

        if msg.message == win32con.WM_NCCALCSIZE:
            return True, 0

        elif msg.message == win32con.WM_NCHITTEST:
            x = GET_X_LPARAM(msg.lParam)
            y = GET_Y_LPARAM(msg.lParam)
            position = self.is_hitting_screen_frame(x, y)
            return True, position
        return False, 0

    def add_shadow(self):
        hwnd = self.get_window_handle()
        margins = struct.pack("@iiii", 200, 200, 200, 200)
        dwm_api = self.load_dwm_api()
        dwm_api.DwmExtendFrameIntoClientArea(hwnd, margins)

    def is_hitting_screen_frame(self, mouse_pos_x, mouse_pos_y):
        border_x = win32api.GetSystemMetrics(win32con.SM_CXFRAME) + win32api.GetSystemMetrics(SM_CXPADDEDBORDER)
        border_y = win32api.GetSystemMetrics(win32con.SM_CYFRAME) + win32api.GetSystemMetrics(SM_CXPADDEDBORDER)

        hwnd = self.get_window_handle()
        rect = win32gui.GetWindowRect(hwnd)
        # print(rect)

        if rect == None or rect == []:
            return win32con.HTNOWHERE

        window_left, window_top, window_right, window_bottom = rect

        client = 0b00000
        left   = 0b00001
        right  = 0b00010
        top    = 0b00100
        bottom = 0b01000
        title_bar = 0b10000

        is_left   = left    * (mouse_pos_x <  (window_left   + border_x))
        is_right  = right   * (mouse_pos_x >= (window_right  - border_x)) 
        is_top    = top     * (mouse_pos_y <  (window_top    + border_y)) 
        is_bottom = bottom  * (mouse_pos_y >= (window_bottom - border_y))
        is_title_bar = title_bar * (mouse_pos_y >  (window_top + border_y) and mouse_pos_y < (window_top + border_y + self.title_bar.height()))

        result = is_left | is_right | is_top | is_bottom | is_title_bar
        if result == left:
            return win32con.HTLEFT
        elif result == right:
            return win32con.HTRIGHT
        elif result == top:
            return win32con.HTTOP
        elif result == bottom:
            return win32con.HTBOTTOM
        elif result == top | left:
            return win32con.HTTOPLEFT
        elif result == top | right:
            return win32con.HTTOPRIGHT
        elif result == bottom | left:
            return win32con.HTBOTTOMLEFT
        elif result == bottom | right:
            return win32con.HTBOTTOMRIGHT
        elif result == client:
            return win32con.HTCLIENT;
        elif result == title_bar:
            return win32con.HTCAPTION;
        else:
            return win32con.HTNOWHERE