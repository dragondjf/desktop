#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
from PyQt5.QtWidgets import QApplication
from desktopframe import DesktopFrame, DesktopItem

if __name__ == '__main__':
    app = QApplication(sys.argv)
    desktop = DesktopFrame()
    app.setStyleSheet(DesktopItem.style)
    desktop.show()
    exitCode = app.exec_()
    sys.exit(exitCode)
