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
    iconChanged = pyqtSignal('QString')
    nameChanged = pyqtSignal('QString')
    zOrderChanged = pyqtSignal(int)

    def __init__(self, icon='', text='', parent=None):
        super(DesktopItem, self).__init__(parent)
        self._icon = icon
        self._name = text
        self._checked = False
        self._hover = False
        self.z = 0

        self.initUI()
        self.initConnect()

    def initUI(self):
        self.setObjectName('normal')
        self.iconLabel = QLabel(self)
        self.iconLabel.setAttribute(Qt.WA_TranslucentBackground)
        self.iconLabel.setPixmap(QPixmap(self._icon))

        self.textLabel = ElideLabel(self._name)
        self.textLabel.setAlignment(Qt.AlignCenter)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.iconLabel)
        mainLayout.addWidget(self.textLabel)
        self.setLayout(mainLayout)
        self.setStyleSheet(self.style)

    def initConnect(self):
        self.iconChanged.connect(self.updateIcon)
        self.zOrderChanged.connect(self.updateName)
        self.nameChanged.connect(self.updateText)

        self.name = self._name

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

    @pyqtProperty('QString', notify=iconChanged)
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value
        self.iconChanged.emit(value)


    @pyqtProperty('QString', notify=nameChanged)
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.nameChanged.emit(value)

    @pyqtProperty(int, notify=zOrderChanged)
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value
        self.zOrderChanged.emit(value)

    def updateName(self, zOrder):
        self.name = str(zOrder)

    def updateText(self, text):
        self.textLabel.setFullText(str(text))

    def updateIcon(self, icon):
        self.iconLabel.setPixmap(QPixmap(self.icon))

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
                item = DesktopItem("skin/images/bvoice.png", str(0), self)
                item.resize(96, 96)
                item.move(96 * i, 96 * j)
                self.items.append(item)

    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

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

    # def getItemByPos(self, pos):
    #     _items = {}
    #     for item in self.items:
    #         if item.geometry().contains(pos):
    #             _items[item.z] = item
    #     if _items:
    #         maxZ = max(_items.keys())
    #         return _items[maxZ]
    #     return None

    def getItemsByPos(self, pos):
        _items = []
        for item in self.items:
            if item.geometry().contains(pos):
                _items.append(item)
        return _items

    def getTopItemByItems(self, items):
        if len(items) == 1:
            return items[0]
        else:
            _item = items[0]
            for i in range(len(items) - 1):
                if items[i + 1].z > _item.z:
                    _item = items[i + 1]
            return _item

    def getTopItemByPos(self, pos):
        _items = self.getItemsByPos(pos)
        if _items:
            return self.getTopItemByItems(_items)
        return None

    def getRelativeItemsByItem(self, item):
        _items = []
        g = item.geometry()
        for _item in self.items:
            if g.intersects(_item.geometry()):
                _items.append(_item)
        return _items

    def getRelativeItemsByRect(self, rect):
        _items = []
        g = rect
        for _item in self.items:
            if g.intersects(_item.geometry()):
                _items.append(_item)
        return _items

    def resetZOrder(self, items):
        print items
        _items = {}
        for item in items:
            _items[item.z] = item

        zKeys = _items.keys()
        zKeys.sort()

        print zKeys

        for i in range(len(zKeys) - 1):
            _items[zKeys[i]].stackUnder(_items[zKeys[i + 1]])

    def checkItemByPos(self, pos):
        for item in self.items:
            if item.geometry().contains(pos):
                item.setChecked(True)
                item.raise_()
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
        # self.setCursor(Qt.CrossCursor)
        # 鼠标点击事件
        pos = event.pos()
        if event.button() == Qt.LeftButton:
            self.pressedEventPos = pos
            self.selectStartPos = pos
            itemsUnderPos = self.getItemsByPos(pos)
            checkedItems = self.getCheckItems()

            # print itemsUnderPos, checkedItems

            if not itemsUnderPos:
                self.setFocus()
                self.clearCheckItems()
            else:
                if len(itemsUnderPos) == 1:
                    if itemsUnderPos[0] in checkedItems:
                        self.startDrag(pos, itemsUnderPos[0])
                    else:
                        self.clearCheckItems()
                        itemsUnderPos[0].setChecked(True)
                        itemsUnderPos[0].raise_()

        super(DesktopFrame, self).mousePressEvent(event)

    def startDrag(self, pos, itemShoudbyChecked):
        oldPos = pos

        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        # dataStream << QPixmap(senderitem._icon)

        mimeData = QMimeData()
        mimeData.setData('application/x-dnditemdata', itemData)


        F = TranslucentFrame()
        F.resize(self.size())
        checkedItems = self.getCheckItems()
        _checkItems = list(item for item in sorted(checkedItems, key=lambda item: item.z))
        for _item in _checkItems:
            item = DesktopItem(_item.icon, _item.name, F)
            item.z = _item.z
            item.resize(96, 96)
            item.move(_item.pos())

        if checkedItems:
            self.dragPixmap = F.grab()

            drag = QDrag(self)
            drag.setDragCursor(QPixmap(), Qt.TargetMoveAction)

            drag.setMimeData(mimeData)
            drag.setPixmap(self.dragPixmap)
            drag.setHotSpot(self.mapFromGlobal(QCursor.pos()))

            action = drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)
            if action == Qt.MoveAction:
                for item in self.items:
                    if item.isChecked():
                        newPos = item.pos() + QCursor.pos() - oldPos

                        newRect = item.geometry()
                        newRect.moveTo(newPos)

                        _items = self.getRelativeItemsByRect(newRect)
                        if item in _items:
                            _items.remove(item)
                        if _items:
                            _topItem = self.getTopItemByItems(_items)
                            if item.z <= _topItem.z:
                                item.z = _topItem.z + 1
                            item.raise_()
                        item.move(newPos)
            else:
                self.clearCheckItems()
                itemShoudbyChecked.setChecked(True)

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
        # if obj is self and event.type() == QEvent.HoverMove:
        #     item = self.getItemsByPos(event.pos())
        #     # print item
        #     if item:
        #         for _item in self.items:
        #             if _item is item:
        #                 _item.setHover(True)
        #             else:
        #                 _item.setHover(False)
        #     else:
        #         for _item in self.items:
        #             _item.setHover(False)
        #     return True
        return super(DesktopFrame, self).eventFilter(obj, event)



if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    desktop = DesktopFrame()
    desktop.show()
    exitCode = app.exec_()
    sys.exit(exitCode)
