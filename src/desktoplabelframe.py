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


class DesktopItem(QLabel):
    style = '''

        QLabel {
            background-color: rgba(0, 0, 0, 0);
            border: 2px solid rgba(0, 0, 0, 0);
            border-radius: 4px;
            color:white
        }

        QLabel#normal{
            background-color: rgba(0, 0, 0, 0);
            border: 2px solid rgba(0, 0, 0, 0);
            border-radius: 4px;
            color:white
        }

        QLabel#hover{
            background-color: rgba(0, 0, 0, 20);
            border: 2px solid rgba(0, 0, 0, 20);
            border-radius: 4px;
            color:white
        }

        QLabel#checked{
            background-color: rgba(0, 0, 0, 80);
            border: 2px solid rgba(100, 100, 100, 80);
            border-radius: 4px;
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
        self._icon = icon
        self._text = text
        self._checked = False
        self._hover = False

        self.initUI()
        self.initConnect()

    def initUI(self):
        self.setObjectName('normal')
        self.iconLabel = QLabel(self)
        self.iconLabel.setAttribute(Qt.WA_TranslucentBackground)
        self.iconLabel.setPixmap(QPixmap(self._icon))

        self.textLabel = ElideLabel(self._text)
        self.textLabel.setAlignment(Qt.AlignCenter)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.iconLabel)
        mainLayout.addWidget(self.textLabel)
        self.setLayout(mainLayout)
        self.setStyleSheet(self.style)

    def initConnect(self):
        pass

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        if self._checked != checked:
            if checked:
                self.setObjectName('checked')
            else:
                self.setObjectName('normal')
            self._checked = checked
            self.setStyleSheet(self.style)

    def setHover(self, hover):
        if self._hover != hover and not self._checked:
            if hover:
                self.setObjectName('hover')
            else:
                self.setObjectName('normal')
            self._hover = hover
            self.setStyleSheet(self.style)



    # def eventFilter(self, obj, event):
    #     if obj is self and event.type() == QEvent.HoverEnter:
    #         self.setHover(True)
    #         return True
    #     elif obj is self and event.type() == QEvent.HoverLeave:
    #         self.setHover(False)
    #         return True
    #     return super(DesktopItem, self).eventFilter(obj, event)


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
        self.setFocus()
        self.setAttribute(Qt.WA_Hover)
        self.installEventFilter(self)

        self.isSelectable = True
        self.selectRect = QRect(0, 0, 0, 0)
        self.selectStartPos = QPoint(0, 0)

        self.pressedEventPos = QPoint(0, 0)

        self.items = []

        for i in xrange(5):
            for j in xrange(5):
                item = DesktopItem("skin/images/bvoice.png", "chromesetWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint) ", self)
                item.resize(96, 96)
                item.move(96 * i, 96 * j)
                self.items.append(item)

        

    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def startDrag(self, pos):
        oldPos = pos

        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        # dataStream << QPixmap(senderitem._icon)

        mimeData = QMimeData()
        mimeData.setData('application/x-dnditemdata', itemData)


        F = TranslucentFrame()
        F.resize(self.size())
        checkedItems = []
        for _item in self.items:
            if _item.isChecked():
                item = DesktopItem(_item._icon, _item._text, F)
                item.resize(96, 96)
                item.move(_item.pos())
                checkedItems.append(item)

        if checkedItems:
            self.dragPixmap = F.grab()

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(self.dragPixmap)
            drag.setHotSpot(self.mapFromGlobal(QCursor.pos()))

            action = drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)
            if action == Qt.MoveAction:
                for item in self.items:
                    if item.isChecked():
                        item.move(item.pos() + QCursor.pos() - oldPos)
            else:
                self.checkItemByPos(pos)
                pass

    def getCheckedRect(self, items):
        xl = []
        yl = []
        xd = {}
        yd = {}

        for item in items:
            xl.append(item.x())
            yl.append(item.y())
            xd.update({item.x(): item})
            yd.update({item.y(): item})

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

    def getItemByPos(self, pos):
        for item in self.items:
            if item.geometry().contains(pos):
                return item
        return None

    def checkItemByPos(self, pos):
        for item in self.items:
            if item.geometry().contains(pos):
                item.setChecked(True)
            else:
                item.setChecked(False)

    def checkItemsByRect(self, rect):
        for item in self.items:
            if rect.intersects(item.geometry()):
                item.setChecked(True)
            else:
                item.setChecked(False)

    def clearCheckItems(self):
        for item in self.items:
            item.setChecked(False)

    def getCheckItems(self):
        checkedItems = []
        for item in self.items:
            if item.isChecked():
                checkedItems.append(item)
        return checkedItems

    def getCheckItemsLength(self):
        return len(self.getCheckItems())

    def isPosInCheckItems(self, pos):
        checkedItems = self.getCheckItems()
        for item in checkedItems:
            if item.geometry().contains(pos):
                return True

    def mousePressEvent(self, event):
        # 鼠标点击事件
        pos = event.pos()
        if event.button() == Qt.LeftButton:
            self.pressedEventPos = pos
            self.selectStartPos = pos
            hasItemUnderPos = self.getItemByPos(pos)
            if not hasItemUnderPos:
                self.setFocus()
                self.clearCheckItems()
            else:
                length = self.getCheckItemsLength()
                if length == 0:
                    self.checkItemByPos(pos)

                if self.isPosInCheckItems(pos):
                    self.startDrag(pos)
                else:
                    self.checkItemByPos(pos)

        super(DesktopFrame, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        self.clearFocus()
        self.update()
        self.pressedEventPos = QPoint(0, 0)
        super(DesktopFrame, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.isSelectable:
            x = self.selectStartPos.x()
            y = self.selectStartPos.y()
            width = event.pos().x() - x
            height = event.pos().y() - y
            self.selectRect = QRect(x, y, width, height)

            self.update()
            self.checkItemsByRect(self.selectRect)

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

    def eventFilter(self, obj, event):
        if obj is self and event.type() == QEvent.HoverMove:
            item = self.getItemByPos(event.pos())
            # print item
            if item:
                for _item in self.items:
                    if _item is item:
                        _item.setHover(True)
                    else:
                        _item.setHover(False)
            else:
                for _item in self.items:
                    _item.setHover(False)
            return True
        return super(DesktopFrame, self).eventFilter(obj, event)



if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    desktop = DesktopFrame()
    desktop.show()
    exitCode = app.exec_()
    sys.exit(exitCode)
