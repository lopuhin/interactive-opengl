# -*- encoding: utf-8 -*-

import sys

from PyQt4 import QtGui

import ui_main


class MainWindow(QtGui.QMainWindow, ui_main.Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
