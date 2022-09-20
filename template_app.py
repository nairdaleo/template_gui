from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenuBar,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QStackedLayout,
    QGroupBox,
    QDockWidget,
    QPushButton,
    QLabel,
    QComboBox,
    QFileDialog,
    QStyle,
)

from PySide6.QtGui import (
    QAction,
    QShortcut,
    QKeySequence,
    QIcon,
)

from PySide6.QtCore import (
    Qt,
    QObject,
    QTimer,
    Signal,
    Slot,
)

import sys
import os
import time
from platform import system
from pathlib import Path
import yaml

VERSION = '0.1a'
WINDOW_TITLE = f'Test app ({VERSION})'
MIN_WINDOW_WIDTH = 600

class MainWindow(QMainWindow, QObject):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumWidth(MIN_WINDOW_WIDTH)
        self.setWindowTitle(WINDOW_TITLE)

        self.mainbox = QGroupBox()
        self.layout = QGridLayout()
        self.mainbox.setLayout(self.layout)

        self._label = QLabel('Hello world!')
        self.layout.addWidget(self._label)

        self.setCentralWidget(self.mainbox)

        if system == 'Darwin':
            self.menu = QMenuBar(None)
            self.setMenuBar(self.menu)
        else:
            self.menu = self.menuBar()

        self.createMenu()
        self.createStatusBar()

        self._currentPath = Path.home()
        self._currentFileName = None

        self.data = {'test' : 'it works!'}

    def createMenu(self):
        ### Add the menu items
        ## File menu
        fileMenu = self.menu.addMenu('File')

        # Menu items
        self.addMenuItem(fileMenu, 'Save', QKeySequence.Save)
        self.addMenuItem(fileMenu, 'Open', QKeySequence.Open)

        # Menu callback
        fileMenu.triggered[QAction].connect(self.fileMenu_cb)

        ## Add more menus the same way. 
        # Check the fileMenu_cb for inspiration on the callbacks 

    def createStatusBar(self):
        self._statusbar = self.statusBar()

        self._selectorbox = QComboBox()
        self._selectorbox.blockSignals(True)
        self._selectorbox.setEditable(True)
        self._selectorbox.setDuplicatesEnabled(False)
        self._selectorbox.currentIndexChanged.connect(self.selectorBoxChanged)
        self._selectorbox.setCurrentIndex(0)
        self._selectorboxItems = []

        self._reloadbutton = QPushButton(QIcon(self.style().standardIcon(QStyle.SP_BrowserReload)),'')
        self._reloadbutton.clicked.connect(self.refresh_SelectorBox)
        self._selectorbox.blockSignals(False)

        self._statusbar.addPermanentWidget(self._selectorbox)
        self._statusbar.addPermanentWidget(self._reloadbutton)

    def addMenuItem(self, menu:QMenuBar, text:str, shortcut:(QShortcut|str) = None):
        _action = QAction(text, self)
        if shortcut is not None:
            _action.setShortcut(shortcut)
        
        menu.addAction(_action)

    def fileMenu_cb(self, event):
        ev_handler = getattr(self, f'file{event.text()}_cb')

        if ev_handler is not None:
            ev_handler()

    def fileSave_cb(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Save File', f'{self._currentPath}', 'YAML (*.yml)')

        if fname != '':
            self._currentFileName = Path(fname)
            self._currentPath = Path(fname).parent

            self.sb_print(f'Saving in {self._currentFileName}')

            with open(f'{self._currentFileName}', 'w') as stream:
                yaml.safe_dump(self.data, stream)

    def fileOpen_cb(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'Open File', f'{self._currentPath}', 'YAML (*.yml)')

        print(f'{fname}, {filter}')

        if fname == '':
            self.sb_print('No file selected')
        else:
            self._currentFileName = Path(fname)
            self.sb_print(f'Opening {self._currentFileName} with filter {filter}')

            with open(f'{self._currentFileName}', 'r') as stream:
                self.data = yaml.safe_load(stream)
                # print(self.data)

            _string = str()
            for k, v in self.data.items():
                _string += f'{k} : {v}'

                if k != list(self.data.keys())[-1]:
                    _string += ', '
            self._label.setText(_string)

    def selectorBoxChanged(self):
        ct = self._selectorbox.currentText()
        ci = self._selectorbox.currentIndex()
        if ct not in self._selectorboxItems:
            self.blockSignals(True)
            self._selectorboxItems.append(ct)
            self.blockSignals(False)
            
        if ci > -1:
            self.sb_print(f'[{ci}] {ct}')
    
    def refresh_SelectorBox(self):
        self.sb_print('Refreshing...')
        self._selectorbox.clear()
        self._selectorboxItems = list()

    def closeEvent(self, event):
        print('Closing window')
        event.accept()

    def sb_print(self, text):
        self._statusbar.showMessage(f'{text}')

if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    try:
        sys.exit(app.exec())
        print("Could not exit")
    finally:
        print('... bye')