from .__about__ import *

from .const import NUKE_VERSION_MAJOR 

if NUKE_VERSION_MAJOR >= 16:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui