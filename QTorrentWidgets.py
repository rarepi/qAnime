from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QTreeWidgetItem, QTreeWidget


class QTorrentTreeWidgetFile(QTreeWidgetItem):
    def __init__(self, file, parent=None):
        super(QTorrentTreeWidgetFile, self).__init__(parent)
        self.file = file
        self.setText(0, self.file.filename)
        self.checked = bool(self.checkState(2))
        self.previous_name = None

        self.setTextColor(0, QColor(128, 128, 128, 255))

        if self.file.filename_new:
            self.setText(1, self.file.filename_new)
            self.checked = self.checkState(2)
        else:
            self.setDisabled(True)

    def setNewName(self, text):
        self.file.filename_new = text

    def setName(self, name:str):
        self.previous_name = self.text(0)
        self.setText(0, name)

    def revertName(self):
        if self.previous_name:
            self.setText(0, self.previous_name)
            self.previous_name = None


class QTorrentTreeWidgetTorrent(QTreeWidgetItem):
    def __init__(self, torrent, parent=None):
        super().__init__(parent)
        self.torrent = torrent
        self.setText(0, self.torrent.name)
        self.checked = bool(self.checkState(2))
        self.previous_name = None

        self.setTextColor(0, QColor(128, 128, 128, 255))

    def setNewName(self, text):
        self.torrent.name_new = text

    def setName(self, name:str):
        self.previous_name = self.text(0)
        self.setText(0, name)

    def revertName(self):
        if self.previous_name:
            self.setText(0, self.previous_name)
            self.previous_name = None

    def addChild(self, child:QTorrentTreeWidgetFile):
        super().addChild(child)

    def child(self, index:int) -> QTorrentTreeWidgetFile:
        return super().child(index)


class QTorrentTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.itemChanged.connect(self.on_item_changed)

    def add_torrent(self, torrent):
        t_widget = QTorrentTreeWidgetTorrent(torrent)
        self.addTopLevelItem(t_widget)

        if len(torrent.files) == 1:                             # suggest new filename as torrent name if there's only one file inside
            t_widget.setText(1, torrent.files[0].filename_new)
            t_widget.setCheckState(2, Qt.Checked)

        if len(torrent.files) >= 1:
            for file in torrent.files:
                f_widget = QTorrentTreeWidgetFile(file, t_widget)
                if file.filename_new:
                    f_widget.setCheckState(2, Qt.Checked)
                else:
                    f_widget.setCheckState(2, Qt.Unchecked)
                t_widget.addChild(f_widget)

    @Slot(QTreeWidgetItem, int)
    def on_item_double_clicked(self, item, column):
        if column == 1:
            flags = item.flags()
            item.setFlags(flags | Qt.ItemIsEditable)
            self.editItem(item, 1)
            item.setFlags(flags)

    @Slot(QTorrentTreeWidgetFile, int)
    @Slot(QTorrentTreeWidgetTorrent, int)
    def on_item_changed(self, item, column):
        if column == 1:
            item.setNewName(item.text(column))
        if column == 2:
            item.checked = bool(item.checkState(column))

    def topLevelItem(self, index) -> QTorrentTreeWidgetTorrent:
        return super().topLevelItem(index)
