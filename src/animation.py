#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class SectionWidget(QFrame):

    style ='''
        QFrame{
            background-color: rgb(88, 197, 1);
        }

        QFrame#content{
            background-color: rgb(255, 197, 1);
        }

    '''

    def __init__(self, sectionTitle, widget, parent=None):
        super(SectionWidget, self).__init__(parent)
        self.parent = parent
        self._sectionTitle = sectionTitle
        self._contentWidget = widget
        self._contentWidget.setObjectName('content')
        self.initUI()
        # self.initAnimation()
        # self.initConnect()

    def initUI(self):
        self.sectionButton = QPushButton(self._sectionTitle)
        self.sectionButton.setFixedHeight(30)
        # self._contentWidget.setFixedHeight(200)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.sectionButton)
        mainLayout.addWidget(self._contentWidget)
        # mainLayout.addStretch()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        self.setStyleSheet(self.style)

        self.sectionHeight = self.sectionButton.height()
        self.expandHeight = 200

        # self._contentWidget.hide()
        # self.setFixedWidth(self.parent.width())
        # self.resize(self.width(), 200)

        self.startGeometry = QRect(self.x(), self.y(), self.width(), 0)
        self.endGeometry = QRect(self.x(), self.y(), self.width(), self.expandHeight)

    # def initAnimation(self):
    #     self.showanimation = QPropertyAnimation(self, 'geometry')
    #     self.showanimation.setStartValue(self.startGeometry)
    #     self.showanimation.setEndValue(self.endGeometry)
    #     self.showanimation.setDuration(1000)
    #     self.showanimation.setEasingCurve(QEasingCurve.OutCubic)

    #     self.hideanimation = QPropertyAnimation(self, 'geometry')
    #     self.hideanimation.setStartValue(self.endGeometry)
    #     self.hideanimation.setEndValue(self.startGeometry)
    #     self.hideanimation.setDuration(1000)
    #     self.hideanimation.setEasingCurve(QEasingCurve.OutCubic)

    # def initConnect(self):
    #     self.sectionButton.clicked.connect(self.toogle)
    #     self.hideanimation.finished.connect(self._contentWidget.hide)
    #     self.showanimation.finished.connect(self.test)

    # def test(self):
    #     print self._contentWidget.height(), self._contentWidget.isVisible()

    # def toogle(self):
    #     # self._contentWidget.setVisible(not self._contentWidget.isVisible())
    #     if self._contentWidget.isVisible():
    #         self.hideanimation.start()
    #     else:
    #         self._contentWidget.show()
    #         self.showanimation.start()


class Frame(QFrame):

    style ='''
        QFrame{
            background-color: rgb(88, 197, 1);
        }

        QFrame#content{
            background-color: rgb(255, 197, 1);
        }

    '''

    def __init__(self, parent=None):
        super(Frame, self).__init__(parent)
        self.resize(800, 600)
        self.moveCenter()

        self.initUI()

    def initUI(self):
        self.section1 = SectionWidget('1', QFrame(), self)
        self.section2 = SectionWidget('2', QFrame(), self)
        self.section3 = SectionWidget('3', QFrame(), self)

        mainLayout = QVBoxLayout()
        # mainLayout.addStretch()
        mainLayout.addWidget(self.section1)
        mainLayout.addWidget(self.section2)
        mainLayout.addWidget(self.section3)
        mainLayout.addStretch()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)
        # self.setStyleSheet(self.style)

       
    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Escape):
            self.close()
        super(Frame, self).keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    desktop = Frame()
    desktop.show()
    exitCode = app.exec_()
    sys.exit(exitCode)
