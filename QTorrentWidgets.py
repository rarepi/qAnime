from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QTreeWidgetItem, QTreeWidget, QWidget, QHBoxLayout, QCheckBox


class QTorrentTreeWidgetFile(QTreeWidgetItem):
    def __init__(self, file, parent=None):
        super(QTorrentTreeWidgetFile, self).__init__(parent)
        self.filename = file.filename
        self.filename_new = file.filename_new

        self.setText(0, self.filename)
        if self.filename_new:
            self.setText(1, self.filename_new)
            self.setCheckState(2, Qt.Checked)
        else:
            self.setDisabled(True)


class QTorrentTreeWidgetTorrent(QTreeWidgetItem):
    def __init__(self, parent=None):
        super(QTorrentTreeWidgetTorrent, self).__init__(parent)
        self.hash = None
        self.files = []
        self.save_path = None


class QTorrentTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(QTorrentTreeWidget, self).__init__()
        self.itemDoubleClicked.connect(self.onTreeWidgetItemDoubleClicked)
        print("called?")

    def add_torrent(self, torrent):
        t_widget = QTorrentTreeWidgetTorrent(self)
        t_widget.setText(0, torrent.name)
        self.addTopLevelItem(t_widget)

        if len(torrent.files) == 1:
            t_widget.setText(1, torrent.files[0].filename_new)
            t_widget.setCheckState(2, Qt.Checked)

        if len(torrent.files) >= 1:
            for file in torrent.files:
                f_widget = QTorrentTreeWidgetFile(file, t_widget)
                t_widget.addChild(f_widget)

    @Slot(QTreeWidgetItem, int)
    def onTreeWidgetItemDoubleClicked(self, item, column):
        item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
        self.editItem(item, 1)
        item.setFlags(Qt.ItemIsEnabled)