#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ElideLabel(QLabel):

    def __init__(self, text, parent=None):
        super(ElideLabel, self).__init__(parent)
        self._fullText = ''
        self.setMinimumWidth(0)
        self.setTextFormat(Qt.PlainText)

        self.setFullText(text)

    def setFullText(self, text):
        self._fullText = text
        self.setText(text)
        self.elideText()

    def elideText(self):
        fm = self.fontMetrics()
        if fm.width(self.text()) != self.width():
            showText = fm.elidedText(self._fullText, Qt.ElideRight, self.width())
            self.setText(showText)

    def resizeEvent(self, event):
        self.elideText()
        super(ElideLabel, self).resizeEvent(event)


class DesktopItem(QPushButton):
    style = '''
        DesktopItem{
            background-color: rgba(0, 0, 0, 0);
            border: None
        }

        DesktopItem:hover{
            background-color: rgba(0, 0, 0, 20);
            border: 2px solid rgba(0, 0, 0, 20);
            border-radius: 4px;
        }

        DesktopItem:checked{
            background-color: rgba(0, 0, 0, 80);
            border: 2px solid rgba(100, 100, 100, 80);
            border-radius: 4px;
        }

        DesktopItem:disabled{
            background-color: gray;
        }

        QLabel {
            background-color: rgba(0, 0, 0, 0);
            color:white
        }

        QLineEdit {
            background-color: rgba(0, 0, 0, 0);
            color:white;
            border: None
        }
    '''

    pressed = pyqtSignal()

    def __init__(self, icon='', text='', parent=None):
        super(DesktopItem, self).__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setFocusPolicy(Qt.NoFocus)
        self.setCheckable(True)

        self._icon = icon
        self._text = text

        self.initUI()
        self.initConnect()

    def initUI(self):
        self.iconLabel = QLabel(self)
        self.iconLabel.setAttribute(Qt.WA_TranslucentBackground)
        self.iconLabel.setPixmap(QPixmap(self._icon))

        self.textLabel = ElideLabel(self._text)
        # self.textLabel.setText(self._text)
        self.textLabel.setAlignment(Qt.AlignCenter)

        # self.textLineEdit = QLineEdit(self._text)
        # self.textLineEdit.setReadOnly(True)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.iconLabel)
        mainLayout.addWidget(self.textLabel)
        self.setLayout(mainLayout)
        # self.setStyleSheet(self.style)

    def initConnect(self):
        # self.clicked.connect(self.updateChecked)
        pass

    # def updateChecked(self):
    #     self.setChecked(True)

    def focusOutEvent(self, event):
        self.setChecked(False)
        super(DesktopItem, self).focusOutEvent(event)

    def mousePressEvent(self, event):
        # 鼠标点击事件
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - \
                self.frameGeometry().topLeft()
            self.setChecked(True)
            self.pressed.emit()

        super(DesktopItem, self).mousePressEvent(event)

    # def mouseReleaseEvent(self, event):
    #     # 鼠标释放事件
    #     if hasattr(self, "dragPosition"):
    #         del self.dragPosition
    #     super(DesktopItem, self).mouseReleaseEvent(event)

    # def mouseMoveEvent(self, event):
    #     if hasattr(self, "dragPosition"):
    #         if event.buttons() == Qt.LeftButton:
    #             self.move(event.globalPos() - self.dragPosition)
    #             print event.pos()
    #     super(DesktopItem, self).mouseMoveEvent(event)

class TranslucentFrame(QFrame):

    def __init__(self, parent=None):
        super(TranslucentFrame, self).__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowState(Qt.WindowMaximized)


class DesktopFrame(TranslucentFrame):

    def __init__(self, parent=None):
        super(DesktopFrame, self).__init__(parent)
        self.setAcceptDrops(True)

        self.isSelectable = True
        self.selectRect = QRect(0, 0, 0, 0)
        self.selectStartPos = QPoint(0, 0)

        self.buttons = []
        self.checkedButtons = []
        for i in xrange(5):
            for j in xrange(5):
                button = DesktopItem("skin/images/bvoice.png", "chromesetWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint) ", self)
                button.resize(96, 96)
                button.move(96 * i, 96 * j)
                
                button.pressed.connect(self.startDrag)
                self.buttons.append(button)


    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def startDrag(self):
        # print('/////////')

        senderButton = self.sender()

        oldPos = senderButton.pos()

        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        dataStream << QPixmap(senderButton._icon)

        mimeData = QMimeData()
        mimeData.setData('application/x-dnditemdata', itemData)


        F = TranslucentFrame()
        F.resize(self.size())
        checkedButtons = []
        for _button in self.buttons:
            if _button.isChecked():
                button = DesktopItem(_button._icon, _button._text, F)
                button.resize(96, 96)
                button.move(_button.pos())
                checkedButtons.append(button)

        if checkedButtons:
            self.dragPixmap = F.grab()

        # for button in checkedButtons:
        #     painter = QPainter()
        #     painter.begin(self.dragPixmap)
        #     painter.fillRect(button.geometry(), QColor(0, 0, 0, 20))
        #     painter.end()

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(self.dragPixmap)
        drag.setHotSpot(self.mapFromGlobal(QCursor.pos()))

        action = drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)
        if action == Qt.MoveAction:
            for button in self.buttons:
                if button.isChecked():
                    button.move(button.pos() + QCursor.pos() - oldPos)
        else:
            pass

    def getCheckedRect(self, buttons):
        xl = []
        yl = []
        xd = {}
        yd = {}

        for button in buttons:
            xl.append(button.x())
            yl.append(button.y())
            xd.update({button.x(): button})
            yd.update({button.y(): button})

        startX = xd[min(xl)].geometry().topLeft().x()
        startY = yd[min(yl)].geometry().topLeft().y()

        endX = xd[max(xl)].geometry().bottomRight().x()
        endY = yd[max(yl)].geometry().bottomRight().y()

        return QRect(startX, startY, endX - startX, endY - startY)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    dragMoveEvent = dragEnterEvent

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            itemData = event.mimeData().data('application/x-dnditemdata')
            dataStream = QDataStream(itemData, QIODevice.ReadOnly)

            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            print('event ignore')
            event.ignore()


    def focusInEvent(self, event):
        self.isSelectable = True
        self.selectRect = QRect(0, 0, 0, 0)
        super(DesktopFrame, self).focusOutEvent(event)

    def focusOutEvent(self, event):
        self.isSelectable = False
        self.selectRect = QRect(0, 0, 0, 0)

        super(DesktopFrame, self).focusOutEvent(event)

    def mousePressEvent(self, event):
        print event
        # 鼠标点击事件
        for button in self.buttons:
            button.setChecked(False)
        if event.button() == Qt.LeftButton:
            self.setFocus()
            self.selectStartPos = event.pos()

        super(DesktopFrame, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.clearFocus()
        self.update()
        super(DesktopFrame, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.isSelectable:
            x = self.selectStartPos.x()
            y = self.selectStartPos.y()
            width = event.pos().x() - x
            height = event.pos().y() - y
            self.selectRect = QRect(x, y, width, height)

            self.update()
            for button in self.buttons:
                if self.selectRect.intersects(button.geometry()):
                    button.setChecked(True)
                else:
                    button.setChecked(False)



        super(DesktopFrame, self).mouseMoveEvent(event)

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Escape):
            self.close()
        super(DesktopFrame, self).keyPressEvent(event)

    def paintEvent(self, event):
        if self.isSelectable:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            color = QColor(0, 0, 0, 90)
            painter.fillRect(self.selectRect, color)
        super(DesktopFrame, self).paintEvent(event)
