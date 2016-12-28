from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtWebKitWidgets import QWebView
import os
from skinned_title_bar import SkinnedTitleBar

# Create an application
app = QApplication([])

# And a window
win = QWidget()
win.setWindowTitle('QWebView Interactive Demo')
win.setWindowFlags(QtCore.Qt.FramelessWindowHint)
#win.setWindowFlags(QtCore.Qt.MSWindowsOwnDC)
#win.setContentsMargins(0, 0, 0, 0)
win.setAttribute(QtCore.Qt.WA_TranslucentBackground)
#a = win.centralWidget()
# And give it a layout
layout = QVBoxLayout()
#layout.setContentsMargins(0, 0, 0, 0)
win.setLayout(layout)
eff = QGraphicsDropShadowEffect()
eff.setBlurRadius(10)
eff.setColor(QtGui.QColor(0,0,0,180))
eff.setOffset(-2, -2)
eff2 = QGraphicsDropShadowEffect()
eff2.setBlurRadius(10)
eff2.setColor(QtGui.QColor(0,0,0,180))
eff2.setOffset(2, 2)
win.setGraphicsEffect(eff)
win.setGraphicsEffect(eff2)

# Create and fill a QWebView
CSS_PATH = "CSS_PATH_VARIABLE"
view = QWebView()
view.page().mainFrame().setScrollBarPolicy(QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)
view.page().mainFrame().setScrollBarPolicy(QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)
with open("index.html","r") as f:
  data = f.read()
  path = os.path.join(os.getcwd(), "css\\main.css")
  path = QUrl.fromLocalFile(path)
  #view.settings().setUserStyleSheetUrl(path)
  #data.replace(CSS_PATH, os.path.join(path,"css\main.css"))
  #view.setHtml(data)
  path = os.path.join(os.getcwd(), "index.html")
  path = QUrl.fromLocalFile(path)
  view.load(path)

# A button to call our JavaScript
button = QPushButton('Set Full Name')

# Interact with the HTML page by calling the completeAndReturnName
# function; print its return value to the console
def complete_name():
    frame = view.page().mainFrame()
    print()

# Connect 'complete_name' to the button's 'clicked' signal
button.clicked.connect(complete_name)

# Add the QWebView and button to the layout
title_bar = SkinnedTitleBar(parent=win, height=20, color_hex="#1E262B")
layout.addWidget(title_bar)
layout.addWidget(view)
layout.setSpacing(0)
#layout.addWidget(button)

frame = view.page().mainFrame()
frame.addToJavaScriptWindowObject('title_bar', title_bar)
# Show the window and run the app
win.show()
app.exec_()
